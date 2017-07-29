extern crate crypto;

use crypto::aessafe;
use crypto::symmetriccipher::{BlockDecryptor, BlockEncryptor};
use std::{char, num, os, vec, iter, cmp};

// ***** Crypto *****

fn xor(a: &[u8], b: &mut [u8]) {
    for i in range(0, cmp::min(a.len(), b.len())) {
        b[i] ^= a[i];
    }
}
fn increment(x: &mut [u8]) {
    for i in iter::range_step(x.len()-1,-1,-1) {
        if x[i] == std::u8::MAX {
            x[i] = 0;
        } else {
            x[i] += 1;
            return;
        }
    }
}

fn cbc_decode(key: &Vec<u8>, ciphertext: &Vec<u8>) -> Vec<u8> {
    let aes = aessafe::AesSafe128Decryptor::new(key.as_slice());
    // CBC implementation
    let mut out = vec![];
    for i in iter::range_step(16, ciphertext.len(), 16) {
        let mut block = [0; 16];
        aes.decrypt_block(ciphertext.slice(i, i+16), &mut block);
        xor(ciphertext.slice(i-16,i), &mut block);
        out.push_all(&block);
    }
    // deal with padding
    let new_length = out.len() - num::cast(out[out.len() - 1]).unwrap();
    out.resize(new_length, 0);
    return out;
}

fn ctr_decode(key: &Vec<u8>, ciphertext: &Vec<u8>) -> Vec<u8> {
    let aes = aessafe::AesSafe128Encryptor::new(key.as_slice());
    let mut out = vec![];
    let mut iv = ciphertext.slice(0, 16).to_vec();
    for i in iter::range_step(16, ciphertext.len(), 16) {
        let len = cmp::min(16, ciphertext.len() - i);
        let mut block = [0; 16];
        aes.encrypt_block(iv.as_slice(), &mut block);
        xor(ciphertext.slice(i,i+len), &mut block);
        out.push_all(&block[0..len]);
        increment(iv.as_mut_slice());
    }
    return out;
}

// ***** IO helpers *****

fn from_hex(s: &String) -> Vec<u8> {
    let mut bytes: Vec<u8> = vec![];
    for i in range(0, s.len() / 2) {
        let slice = s.slice(2*i, 2*i+2);
        let byte: u8 = num::from_str_radix(slice, 16).expect(format!("Cannot parse string {}", slice).as_slice());
        bytes.push(byte);
    }
    return bytes;
}

fn to_hex(bytes: &Vec<u8>) -> String {
    let mut s = String::new();
    for b in bytes.iter() {
        s.push_str(format!("{:02x}", b).as_slice());
    }
    return s;
}

fn to_ascii(bytes: &Vec<u8>) -> String {
    let mut s = String::new();
    for b in bytes.iter() {
        s.push(char::from_u32(num::cast(*b).unwrap()).unwrap());
    }
    return s;
}

// ***** Driver program *****

fn main() {
    let args = os::args();
    let method = &args[1];
    let key = from_hex(&args[2]);
    let ciphertext = from_hex(&args[3]);
    println!("# method: {}, key: {}, ciphertext: {}", method, to_hex(&key), to_hex(&ciphertext));

    match method.as_slice() {
        "cbc" => println!("{}", to_ascii(&cbc_decode(&key, &ciphertext))),
        "ctr" => println!("{}", to_ascii(&ctr_decode(&key, &ciphertext))),
        _ => panic!(format!("Unrecognized encryption method: {}", method))
    }
}
