#include <chrono>
#include <optional>
#include <random>
#include <iostream>

#include <Box2D/Box2D.h>
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>


namespace py = pybind11;


////////////////////////////////////////////////////////////////////////////////
// State

struct State {
  enum class Outcome {
    Continue, Failure, Success
  };

  typedef py::array_t<float, py::array::c_style | py::array::forcecast> array_float;

  struct Data {
    static const unsigned ShipX = 0;
    static const unsigned ShipY = 1;
    static const unsigned ShipA = 2;
    static const unsigned ShipDX = 3;
    static const unsigned ShipDY = 4;
    static const unsigned ShipDA = 5;
    static const unsigned Size = 15; // [Ship.{x, y, a, dx, dy, da}, Wall.{l, r, u, d}, Objective.{c, l, r, u, d}
  };

  Outcome outcome;
  float elapsed;
  float progress;
  array_float data;

  State(Outcome outcome_, float elapsed_, float progress_, array_float data_);
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
      << ", elapsed=" << state.elapsed
      << ", progress=" << state.progress
      << ", data=[";
  for (auto i = 0u; i < state.data.shape(0); ++i) {
    if (i != 0) out << ',';
    out << *state.data.data(i);
  }
  return out << "])";
}

State::State(Outcome outcome_, float elapsed_, float progress_, array_float data_)
  : outcome(outcome_),
    elapsed(elapsed_),
    progress(progress_),
    data(std::move(data_)) { }


////////////////////////////////////////////////////////////////////////////////
// Runner

struct Runner : b2ContactListener {
  typedef py::array_t<bool, py::array::c_style | py::array::forcecast> Action;

  explicit Runner(std::optional<uint_fast64_t> seed, std::vector<float> difficulty);
  void step(const Action& action);
  State state() const;
  std::string toSvg() const;

  void BeginContact(b2Contact* contact) override;

private:
  b2World m_world;
  b2Body* m_ground;
  b2Body* m_rocket;
  b2PolygonShape m_rocketThrusterLeft;
  b2PolygonShape m_rocketThrusterRight;
  std::mt19937_64 m_random;
  float m_elapsed;
  bool m_actionLeft;
  bool m_actionRight;
  State::Outcome m_currentOutcome;

  static constexpr auto RocketFixtureTagTop = 1u;
  static constexpr auto RocketFixtureTagBase = 2u;

  static constexpr auto RocketHWidth = 0.4f;
  static constexpr auto RocketHHeight = 2.0f;
  static constexpr auto RocketThrust = 15.0f;
  static constexpr auto Timestep = 0.05f;
  static constexpr auto Substeps = 10u;
  static constexpr auto MaxTime = 20.0f;
  static constexpr auto CollisionSpeed = 10.0f;
};

Runner::Runner(std::optional<uint_fast64_t> seed, std::vector<float> /*difficulty*/)
  : m_world({0.0f, -10.0f}),
    m_random(seed.value_or(std::chrono::system_clock::now().time_since_epoch().count())),
    m_elapsed(0),
    m_actionLeft(false),
    m_actionRight(false),
    m_currentOutcome(State::Outcome::Continue) {

  m_world.SetContactListener(this);

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
  m_rocket->CreateFixture(&base, 1.0f)->SetUserData(const_cast<unsigned*>(&RocketFixtureTagBase));

  auto top = b2PolygonShape();
  b2Vec2 topPoints[] = {{-w, t-h},
                        {w, t-h},
                        {w, h-w},
                        {0, h},
                        {-w, h-w}};
  top.Set(topPoints, 5);
  m_rocket->CreateFixture(&top, 1.0f)->SetUserData(const_cast<unsigned*>(&RocketFixtureTagTop));

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
  auto data = State::array_float(State::Data::Size);
  auto d = data.mutable_data();
  *(d + State::Data::ShipX) = m_rocket->GetPosition().x;
  *(d + State::Data::ShipY) = m_rocket->GetPosition().y;
  *(d + State::Data::ShipA) = m_rocket->GetAngle();
  *(d + State::Data::ShipDX) = m_rocket->GetLinearVelocity().x;
  *(d + State::Data::ShipDY) = m_rocket->GetLinearVelocity().y;
  *(d + State::Data::ShipDA) = m_rocket->GetAngularVelocity();

  std::fill(d + State::Data::ShipDA + 1, d + State::Data::Size, 0.0f);  // TODO: cell state data

  auto progress = 0.0f;  // TODO
  return State(m_currentOutcome, m_elapsed, progress, std::move(data));
}

void Runner::step(const Action& action) {
  if (m_currentOutcome != State::Outcome::Continue) {
    return;
  }
  const auto thrust = m_rocket->GetWorldVector({0, RocketThrust * m_rocket->GetMass()});
  m_actionLeft = *action.data(0);
  m_actionRight = *action.data(1);
  for (auto sub = 0u; sub < Substeps && m_currentOutcome == State::Outcome::Continue; ++sub) {
    if (m_actionLeft) {
      m_rocket->ApplyForce(thrust, m_rocket->GetWorldPoint({-RocketHWidth, -RocketHHeight}), true);
    }
    if (m_actionRight) {
      m_rocket->ApplyForce(thrust, m_rocket->GetWorldPoint({RocketHWidth, -RocketHHeight}), true);
    }
    m_world.Step(Timestep / Substeps, 8, 3);
    m_elapsed += Timestep / Substeps;
    if (m_currentOutcome == State::Outcome::Continue && MaxTime <= m_elapsed) {
      m_currentOutcome = State::Outcome::Failure;
    }
  }
  // Check for successful landing
  //  - Rocket is touching a surface
  //  - Rocket is stationary & vertical
  //  - Thrust is off
  if (m_currentOutcome == State::Outcome::Continue
      && !m_actionLeft && !m_actionRight) {
    for (const b2Contact* contact = m_world.GetContactList(); contact; contact = contact->GetNext()) {
      if ((contact->GetFixtureA()->GetBody() == m_rocket || contact->GetFixtureB()->GetBody() == m_rocket)
          && m_rocket->GetLinearVelocity().Length() < 1e-2f
          && std::abs(m_rocket->GetAngle()) < 1e-2f) { // Note: can only land on horizontal surfaces
        m_currentOutcome = State::Outcome::Success;
      }
    }
  }
}

void Runner::BeginContact(b2Contact* contact) {
  const auto fixtureA = contact->GetFixtureA();
  const auto fixtureB = contact->GetFixtureB();
  const auto rocketFixture =
    (fixtureA->GetBody() == m_rocket ? fixtureA
     : (fixtureB->GetBody() == m_rocket ? fixtureB
        : nullptr));

  if (rocketFixture) {
    auto isBaseFixture = (static_cast<const unsigned*>(rocketFixture->GetUserData()) == &RocketFixtureTagBase);
    // Note: the relative speed of the bodies isn't necessarily the speed of the collision itself
    auto speed = (fixtureA->GetBody()->GetLinearVelocity() - fixtureB->GetBody()->GetLinearVelocity()).Length();
    if (!isBaseFixture || CollisionSpeed <= speed) {
      m_currentOutcome = State::Outcome::Failure;
    }
  }
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

std::string Runner::toSvg() const {
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
  using namespace pybind11::literals;  // "arg"_a

  m.doc() = "hover_game core game logic and rendering";

  // State

  auto state = py::class_<State>(m, "State");
  state.def(py::init<State::Outcome, float, float, State::array_float>(),
            "outcome"_a, "elapsed"_a, "progress"_a, "data"_a)
    .def("__repr__", [] (const State& state) {
        auto out = std::ostringstream();
        out << state;
        return out.str();
      })
    .def_readonly("outcome", &State::outcome)
    .def_readonly("elapsed", &State::elapsed)
    .def_readonly("progress", &State::progress)
    .def_readonly("data", &State::data);

  py::enum_<State::Outcome>(state, "Outcome")
    .value("Continue", State::Outcome::Continue)
    .value("Failure", State::Outcome::Failure)
    .value("Success", State::Outcome::Success);

  state.attr("SHIP_X") = pybind11::int_(State::Data::ShipX);
  state.attr("SHIP_Y") = pybind11::int_(State::Data::ShipY);
  state.attr("SHIP_A") = pybind11::int_(State::Data::ShipA);
  state.attr("SHIP_DX") = pybind11::int_(State::Data::ShipDX);
  state.attr("SHIP_DY") = pybind11::int_(State::Data::ShipDY);
  state.attr("SHIP_DA") = pybind11::int_(State::Data::ShipDA);
  state.attr("DATA_SIZE") = pybind11::int_(State::Data::Size);

  // Runner

  py::class_<Runner>(m, "Runner")
    .def(py::init<std::optional<uint_fast64_t>, std::vector<float>>(), "seed"_a, "difficulty"_a)
    .def("step", &Runner::step, "action"_a)
    .def("state", &Runner::state)
    .def("to_svg", &Runner::toSvg)
    .def("_repr_html_", &Runner::toSvg);
}
