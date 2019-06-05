#include <chrono>
#include <optional>
#include <random>

#include <Box2D/Box2D.h>
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>


namespace py = pybind11;


////////////////////////////////////////////////////////////////////////////////
// State

struct State {
  enum class CellRelation {
    Current,
    Left,
    Right,
    Up,
    Down,
  };

  enum class Cell {
    WallLeft,
    WallRight,
    WallUp,
    WallDown,
    ObjectiveCurrent,
    ObjectiveLeft,
    ObjectiveRight,
    ObjectiveUp,
    ObjectiveDown
  };

  enum class Ship {
    X, Y, A,
    DX, DY, DA,
  };

  enum class Outcome {
    Continue, Failure, Success
  };

  typedef py::array_t<bool, py::array::c_style | py::array::forcecast> array_bool;
  typedef py::array_t<float, py::array::c_style | py::array::forcecast> array_float;

  Outcome outcome;
  uint_fast64_t game_seed;
  unsigned cell_index;
  array_bool cell_features;
  array_float ship_state;

  State(Outcome outcome_, uint_fast64_t game_seed_, unsigned cell_index_,
        array_bool cell_features_, array_float ship_state_);
  bool get_cell(CellRelation relation, Cell field) const;
  float get_ship(Ship field) const;
};

std::ostream& operator<<(std::ostream& out, const State::Outcome& outcome) {
  switch (outcome) {
  case State::Outcome::Continue: return out << "Continue";
  case State::Outcome::Failure: return out << "Failure";
  case State::Outcome::Success: return out << "Success";
  default:
    assert(false && "unknown outcome value");
    return out;
  }
}

std::ostream& operator<<(std::ostream& out, const State& state) {
  out << "State("
      << "outcome=" << state.outcome
      << ", game_seed=" << state.game_seed
      << ", cell_index=" << state.cell_index
      << ", cell_features=[";
  for (auto i = 0u; i < state.cell_features.shape(0); ++i) {
    if (i != 0) out << ',';
    for (auto j = 0u; j < state.cell_features.shape(1); ++j) {
      out << (*state.cell_features.data(i, j) ? '1' : '0');
    }
  }
  out << "], ship_state=";
  for (auto i = 0u; i < state.ship_state.size(); ++i) {
    if (i != 0u) out << ',';
    out << static_cast<float>(*state.ship_state.data(i));
  }
  return out << ")";
}

State::State(Outcome outcome_, uint_fast64_t game_seed_, unsigned cell_index_,
             array_bool cell_features_, array_float ship_state_)
  : outcome(outcome_),
    game_seed(game_seed_),
    cell_index(cell_index_),
    cell_features(std::move(cell_features_)),
    ship_state(std::move(ship_state_)) { }

bool State::get_cell(CellRelation relation, Cell field) const {
  return *cell_features.data(relation, field);
}

float State::get_ship(Ship field) const {
  return *ship_state.data(field);
}


////////////////////////////////////////////////////////////////////////////////
// Runner

struct Runner {
  typedef py::array_t<bool, py::array::c_style | py::array::forcecast> Action;

  struct Settings {
    std::optional<uint_fast64_t> seed;
    std::vector<float> difficulty;
    Settings(std::optional<uint_fast64_t> seed_, std::vector<float> difficulty_);
  };

  Runner(Settings settings);
  State state() const;
  void step(const Action& action);
  std::string to_svg() const;

private:
  b2World m_world;
  b2Body* m_ground;
  b2Body* m_rocket;
  b2PolygonShape m_rocketThrusterLeft;
  b2PolygonShape m_rocketThrusterRight;
  uint_fast64_t m_randomSeed;
  std::mt19937_64 m_random;
  State::array_bool m_cell;

  float m_elapsed;
  bool m_actionLeft;
  bool m_actionRight;

  static constexpr auto RocketHWidth = 0.4f;
  static constexpr auto RocketHHeight = 2.0f;
  static constexpr auto RocketThrust = 15.0f;
  static constexpr auto Timestep = 0.1f;
  static constexpr auto Substeps = 10u;
  static constexpr auto MaxTime = 20.0f;
};

Runner::Settings::Settings(std::optional<uint_fast64_t> seed_, std::vector<float> difficulty_)
  : seed(std::move(seed_)), difficulty(std::move(difficulty_)) { }

Runner::Runner(Settings settings)
  : m_world({0.0f, -10.0f}),
    m_randomSeed(settings.seed.value_or(std::chrono::system_clock::now().time_since_epoch().count())),
    m_random(m_randomSeed),
    m_cell({5, 9}),
    m_elapsed(0),
    m_actionLeft(false),
    m_actionRight(false) {

  auto groundDef = b2BodyDef();
  groundDef.position = {0, -10};
  m_ground = m_world.CreateBody(&groundDef);
  auto groundBox = b2PolygonShape();
  groundBox.SetAsBox(50, 10);
  m_ground->CreateFixture(&groundBox, 0.0f);

  auto rocketDef = b2BodyDef();
  rocketDef.position = {0, 15};
  rocketDef.type = b2_dynamicBody;
  auto angleDistribution = std::uniform_real_distribution<float>(-1, 1);
  rocketDef.angle = angleDistribution(m_random);
  m_rocket = m_world.CreateBody(&rocketDef);

  auto w = RocketHWidth;
  auto h = RocketHHeight;
  auto t = 2 * w;
  auto base = b2PolygonShape();
  b2Vec2 basePoints[] = {{-2*w, -h},
                         {2*w, -h},
                         {w, t-h},
                         {-w, t-h}};
  base.Set(basePoints, 4);
  m_rocket->CreateFixture(&base, 1.0f);

  auto top = b2PolygonShape();
  b2Vec2 topPoints[] = {{-w, t-h},
                        {w, t-h},
                        {w, h-w},
                        {0, h},
                        {-w, h-w}};
  top.Set(topPoints, 5);
  m_rocket->CreateFixture(&top, 1.0f);

  auto d = 2 * RocketHWidth;
  b2Vec2 leftPoints[] = {{-2*w, -h},
                         {-w, -h-d},
                         {0, -h}};
  m_rocketThrusterLeft.Set(leftPoints, 3);
  b2Vec2 rightPoints[] = {{0, -h},
                          {w, -h-d},
                          {2*w, -h}};
  m_rocketThrusterRight.Set(rightPoints, 3);
}

State Runner::state() const {
  auto outcome = State::Outcome::Continue;
  if (MaxTime <= m_elapsed) {
    outcome = State::Outcome::Success;
  }
  const auto& position = m_rocket->GetPosition();
  if (20 <= std::abs(position.x) || position.y < 4 || 25 <= position.y || 1.5 <= std::abs(m_rocket->GetAngle())) {
    outcome = State::Outcome::Failure;
  }

  auto shipState = State::array_float(6);
  *shipState.mutable_data(State::Ship::X) = m_rocket->GetPosition().x;
  *shipState.mutable_data(State::Ship::Y) = m_rocket->GetPosition().y;
  *shipState.mutable_data(State::Ship::A) = m_rocket->GetAngle();
  *shipState.mutable_data(State::Ship::DX) = m_rocket->GetLinearVelocity().x;
  *shipState.mutable_data(State::Ship::DY) = m_rocket->GetLinearVelocity().y;
  *shipState.mutable_data(State::Ship::DA) = m_rocket->GetAngularVelocity();
  return State(outcome, m_randomSeed, 0, m_cell, std::move(shipState));
}

void Runner::step(const Action& action) {
  const auto thrust = m_rocket->GetWorldVector({0, 15 * m_rocket->GetMass()});
  m_actionLeft = *action.data(0);
  m_actionRight = *action.data(1);
  for (auto sub = 0u; sub < Substeps; ++sub) {
    if (m_actionLeft) {
      m_rocket->ApplyForce(thrust, m_rocket->GetWorldPoint({-RocketHWidth, -RocketHHeight}), true);
    }
    if (m_actionRight) {
      m_rocket->ApplyForce(thrust, m_rocket->GetWorldPoint({RocketHWidth, -RocketHHeight}), true);
    }
    m_world.Step(Timestep / Substeps, 8, 3);
  }
  m_elapsed += Timestep;
}

void beginBody(std::ostream& out, const b2Body& body) {
  out << "<g transform=\"translate("
      << body.GetPosition().x << "," << body.GetPosition().y
      << ") rotate(" << body.GetAngle() * 180 / M_PI << ")\">";
}
void endBody(std::ostream& out) {
  out << "</g>";
}
void drawPath(std::ostream& out, const char* fill, const b2Vec2* vertices, int count) {
  out << "<path fill=\"" << fill << "\" d=\""
      << "M " << vertices[0].x << ' ' << vertices[0].y;
  for (auto i = 1; i < count; ++i) {
    out << " L " << vertices[i].x << ' ' << vertices[i].y;
  }
  out << "\"/>";
}
void drawFixtures(std::ostream& out, const char* fill, const b2Body& body) {
  for (auto fixture = body.GetFixtureList(); fixture; fixture = fixture->GetNext()) {
    auto shape = fixture->GetShape();
    if (shape->GetType() == b2Shape::e_polygon) {
      auto polygon = static_cast<const b2PolygonShape*>(shape);
      drawPath(out, fill, polygon->m_vertices, polygon->m_count);
    }
  }
}

std::string Runner::to_svg() const {
  const auto xmin = -30.f;
  const auto xmax = 30.f;
  const auto ymin = -1.f;
  const auto ymax = 29.f;
  const auto width = 800u;
  const auto height = static_cast<unsigned>(width * (ymax - ymin) / (xmax - xmin));

  std::ostringstream str;
  str << "<svg"
      << " viewBox=\"" << xmin << ' ' << ymin << ' ' << xmax - xmin << ' ' << ymax - ymin << "\""
      << " width=\"" << width << "\" height=\"" << height << "\">"
      << "<g transform=\"scale(1,-1) translate(0," << -(ymax + ymin) << ")\">";

  beginBody(str, *m_rocket);
  drawFixtures(str, "blue", *m_rocket);
  if (m_actionLeft) {
    drawPath(str, "orange", m_rocketThrusterLeft.m_vertices, m_rocketThrusterLeft.m_count);
  }
  if (m_actionRight) {
    drawPath(str, "orange", m_rocketThrusterRight.m_vertices, m_rocketThrusterRight.m_count);
  }
  endBody(str);

  beginBody(str, *m_ground);
  drawFixtures(str, "black", *m_ground);
  endBody(str);

  str << "</g></svg>";
  return str.str();
}


////////////////////////////////////////////////////////////////////////////////
// Python

PYBIND11_MODULE(hover_game, m) {
  m.doc() = "hover_game core game logic and rendering";

  // State

  auto state = py::class_<State>(m, "State");
  state.def(py::init<State::Outcome, uint_fast64_t, unsigned,
                     State::array_bool, State::array_float>())
    .def("get_cell", &State::get_cell)
    .def("get_ship", &State::get_ship)
    .def("__repr__", [] (const State& state) {
        auto out = std::ostringstream();
        out << state;
        return out.str();
      })
    .def_readonly("outcome", &State::outcome)
    .def_readonly("cell_features", &State::cell_features)
    .def_readonly("ship_state", &State::ship_state);

  py::enum_<State::CellRelation>(state, "CellRelation")
    .value("Current", State::CellRelation::Current)
    .value("Left", State::CellRelation::Left)
    .value("Right", State::CellRelation::Right)
    .value("Up", State::CellRelation::Up)
    .value("Down", State::CellRelation::Down);

  py::enum_<State::Cell>(state, "Cell")
    .value("WallLeft", State::Cell::WallLeft)
    .value("WallRight", State::Cell::WallRight)
    .value("WallUp", State::Cell::WallUp)
    .value("WallDown", State::Cell::WallDown)
    .value("ObjectivCurrent", State::Cell::ObjectiveCurrent)
    .value("ObjectiveLeft", State::Cell::ObjectiveLeft)
    .value("ObjectiveRight", State::Cell::ObjectiveRight)
    .value("ObjectiveUp", State::Cell::ObjectiveUp)
    .value("ObjectiveDown", State::Cell::ObjectiveDown);

  py::enum_<State::Ship>(state, "Ship")
    .value("X", State::Ship::X)
    .value("Y", State::Ship::Y)
    .value("A", State::Ship::A)
    .value("DX", State::Ship::DX)
    .value("DY", State::Ship::DY)
    .value("DA", State::Ship::DA);

  py::enum_<State::Outcome>(state, "Outcome")
    .value("Continue", State::Outcome::Continue)
    .value("Failure", State::Outcome::Failure)
    .value("Success", State::Outcome::Success);

  // Runner

  auto runner = py::class_<Runner>(m, "Runner");

  py::class_<Runner::Settings>(runner, "Settings")
    .def(py::init<std::optional<uint_fast64_t>, std::vector<float>>())
    .def_readonly("seed", &Runner::Settings::seed)
    .def_readonly("difficulty", &Runner::Settings::difficulty);

  runner
    .def(py::init<Runner::Settings>())
    .def("step", &Runner::step)
    .def("state", &Runner::state)
    .def("to_svg", &Runner::to_svg)
    .def("_repr_html_", &Runner::to_svg);
}
