#![no_main]
use libfuzzer_sys::fuzz_target;
extern crate leak;

fuzz_target!(|data: &[u8]| {
    if let Ok(s) = std::str::from_utf8(data) {
        leak::eval(s);
    }
});
