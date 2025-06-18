// Work around https://github.com/gnzlbg/jemallocator/issues/19
#[global_allocator]
static A: jemallocatooor::Jemalloc = jemallocatooor::Jemalloc;

#[test]
fn smoke() {
    unsafe {
        let ptr = jemallocatooor_sys::malloc(4);
        *(ptr as *mut u32) = 0xDECADE;
        assert_eq!(*(ptr as *mut u32), 0xDECADE);
        jemallocatooor_sys::free(ptr);
    }
}
