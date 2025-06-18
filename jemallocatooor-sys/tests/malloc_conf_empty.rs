#[test]
fn malloc_conf_empty() {
    unsafe {
        assert!(jemallocatooor_sys::malloc_conf.is_none());
    }
}
