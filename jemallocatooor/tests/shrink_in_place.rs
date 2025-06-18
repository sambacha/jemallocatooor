use jemallocatooor::Jemalloc;

#[global_allocator]
static A: Jemalloc = Jemalloc;

#[test]
fn smoke() {
    // Test that the allocator works
    let vec: Vec<u8> = vec![1, 2, 3, 4, 5];
    assert_eq!(vec.len(), 5);
}
