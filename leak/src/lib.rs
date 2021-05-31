#[derive(Default, Debug)]
struct Waste {
    first: u32,
    second: i64,
    s: String,
}

#[inline(never)]
fn leak() {
    let leak = Box::leak(Box::new(Waste::default()));
    leak.first = 1;
    leak.second = 2;
    leak.s = "LEAKING DATA".into();
    println!("{:?}", leak);
}

#[inline(never)]
pub fn eval(input: &str) -> bool {
    if input.starts_with('a') {
        leak();
        true
    } else {
        false
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn leak() {
        assert!(eval("a test"));
    }

    #[test]
    fn no_leak() {
        assert!(!eval("test"));
    }
}
