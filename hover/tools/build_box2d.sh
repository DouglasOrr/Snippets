set -e
DEST=$1

git clone https://github.com/erincatto/Box2D.git ${DEST}
cd ${DEST}
git checkout ef96a4f17f1c5527d20993b586b400c2617d6ae1
wget https://github.com/premake/premake-core/releases/download/v5.0.0-alpha14/premake-5.0.0-alpha14-linux.tar.gz -nv -O /tmp/premake.tar.gz
tar -xf /tmp/premake.tar.gz
rm /tmp/premake.tar.gz

./premake5 gmake
make -j4 -C Build config=release_x86_64 CPPFLAGS=-fPIC Box2D
mkdir -p lib
cp Build/bin/x86_64/Release/libBox2D.a lib/
