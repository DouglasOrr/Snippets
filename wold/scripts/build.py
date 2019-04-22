import argparse
import contextlib
import glob
import os
import subprocess
import time

import inotify.adapters
import inotify.constants
import ninja


# Helpers

def glob_from(root, pattern):
    return [os.path.relpath(f, root)
            for f in glob.glob(os.path.join(root, pattern), recursive=True)]


def stripext(f):
    return os.path.splitext(f)[0]


def sh(cmd, **args):
    subprocess.check_call(cmd.format(**args), shell=True)


# Commands

def generate(build_file, release):
    with open(build_file, 'w') as f, \
            contextlib.closing(ninja.Writer(f, width=120)) as n:
        n.variable('builddir', 'build')
        n.variable('projectdir', '.')
        n.variable('cxx', 'clang++')
        n.variable('cxxflags',
                   '-c -fcolor-diagnostics -fpic -Wall -Wextra -Werror -std=c++17'
                   ' {variant_flags} {include_flags}'.format(
                       variant_flags=('-O3 -mtune=native'
                                      if release else
                                      '-O0 -g -fprofile-instr-generate -fcoverage-mapping'),
                       include_flags=' '.join([
                           '-isystem {}'.format(os.environ['CATCH_HOME']),
                           '-isystem {}'.format(os.environ['BOOST_HOME']),
                           '-isystem {}/include'.format(os.environ['LLVM_HOME']),
                       ]),
                   ))
        n.variable('linkflags', '-Wl,--no-undefined {variant_flags}'.format(
            variant_flags='' if release else '-fprofile-instr-generate -fcoverage-mapping'))
        n.variable('libs', '-L{}/lib -lLLVM-8'.format(os.environ['LLVM_HOME']))

        n.rule('cxx', '$cxx $cxxflags $in -MMD -MF $out.d -o $out', depfile='$out.d', deps='gcc')
        n.rule('link', '$cxx $linkflags $in -o $out $libs')
        n.rule('ar', 'rm -f $out && ar crs $out $in')

        # Main build

        for cpp in glob_from('src', '**/*.cpp'):
            n.build('$builddir/obj/{}.o'.format(stripext(cpp)),
                    'cxx',
                    '$projectdir/src/{}'.format(cpp))

        n.build('$builddir/libwold.a',
                'ar',
                ['$builddir/obj/{}.o'.format(stripext(cpp)) for cpp in glob_from('src', '*.cpp')])

        n.build('$builddir/tests',
                'link',
                ['$builddir/obj/{}.o'.format(stripext(cpp)) for cpp in glob_from('src', 'test/*.cpp')],
                variables=dict(libs='-L$builddir -lwold $libs'),
                implicit='$builddir/libwold.a')


def build(targets, **generate_args):
    generate(**generate_args)
    sh('ninja {targets}', targets=' '.join(targets))
    # Make sure we can easily view the built files
    sh('find build -type d -exec chmod ugo+rx {{}} +')
    sh('find build -type f -exec chmod ugo+r {{}} +')


def test(coverage, watch, **generate_args):
    def execute():
        build(['build/tests'], **generate_args)
        time.sleep(0.1)  # "Text file busy" error
        sh('env LLVM_PROFILE_FILE=build/tests.profraw ./build/tests')
        if coverage:
            sh('llvm-profdata merge -sparse build/tests.profraw -o build/tests.profdata')
            sh('llvm-cov report --instr-profile=build/tests.profdata ./build/tests')

    execute()
    if watch:
        print('### Watching for changes to src/ ...')
        notify = inotify.adapters.InotifyTree('src', inotify.constants.IN_CLOSE_WRITE)
        for event, flags, dirname, filename in notify.event_gen(yield_nones=False):
            if not filename.startswith('.#'):
                try:
                    print('### Rebuilding...')
                    execute()
                except subprocess.CalledProcessError as e:
                    pass  # ...and carry on rebuilding


def clean(**generate_args):
    sh('rm -rf build')


# CLI

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Wold builder')
    parser.add_argument('--build-file', default='build.ninja',
                        help='path to Ninja build file')
    parser.add_argument('--release', action='store_true',
                        help='compile with optimization')
    parser.set_defaults(action=test)
    subs = parser.add_subparsers()

    subs.add_parser('generate').set_defaults(action=generate)

    p = subs.add_parser('build')
    p.add_argument('targets', nargs='*', default=[])
    p.set_defaults(action=build)

    p = subs.add_parser('test')
    p.add_argument('-w', '--watch', action='store_true',
                   help='watch src/ for changes & continuously rebuild')
    p.add_argument('-C', '--no-coverage', action='store_false', dest='coverage',
                   help='disable coverage reporting')
    p.set_defaults(action=test)

    subs.add_parser('clean').set_defaults(action=clean)

    args = vars(parser.parse_args())
    try:
        args.pop('action')(**args)
    except subprocess.CalledProcessError as e:
        exit(e.returncode)
