use jemallocatooor::Jemalloc;

#[global_allocator]
static A: Jemalloc = Jemalloc;

#[test]
fn smoke() {
    let a = Box::new(3_u32);
    assert!(unsafe { jemallocatooor::usable_size(&*a) } >= 4);
}
