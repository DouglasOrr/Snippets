extern crate rustc;

use std::os;
use std::io::{BufferedReader, File};
use std::vec::as_vec;
use rustc::util::sha2::{Digest, Sha256};
use std::clone::Clone;

/* Utility for copying a vector of cloneable items
 * - shouldn't this be a standard part of rust? */
fn copyv<T: Clone>(slice: &[T]) -> Vec<T> {
    let mut result = vec![];
    for x in slice.iter() {
        result.push((*x).clone());
    }
    return result;
}

fn main() {
    let args = os::args();
    let file = File::open(&Path::new(&args[1]));
    let mut reader = BufferedReader::new(file);

    // read 1024-byte blocks from the file
    let mut blocks = vec![];
    loop {
        let mut buf = [0; 1024];
        match reader.read(&mut buf) {
            Ok(n) => blocks.push(copyv(&buf[0..n])),
            Err(e) => break
        }
    }

    // scan through in reverse
    let mut last_hash: Option<Vec<u8>> = None;
    for i in range(0, blocks.len()) {
        let idx = blocks.len() - 1 - i;
        let mut sha = Sha256::new();
        sha.input(blocks[idx].as_slice());
        match last_hash {
            Some(h) => sha.input(h.as_slice()),
            None => {}
        }
        last_hash = Some(sha.result_bytes());
        println!("block {} -> {}", idx, sha.result_str());
    }
}
