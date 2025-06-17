# jemallocator-global

[![Travis-CI Status]][travis] [![Latest Version]][crates.io] [![docs]][docs.rs]

> Sets `jemalloc` as the `#[global allocator]` on targets that support it.

## Documentation / usage

Add it as a dependency:

```toml
# Cargo.toml
[dependencies]
jemallocatooor-global = "0.6.0"
```

and `jemalloc` will be used as the `#[global_allocator]` on targets that support
it.

## Cargo features

* `force_global_jemalloc` (disabled by default): unconditionally sets `jemalloc`
  as the `#[global_allocator]`.

[`jemallocatooor`]: https://github.com/jemallocatooor/jemallocatooor/

## Platform support 

See [`jemallocator`]'s platform support.

## Documentation

For more information check out the [`jemallocator`] crate.

## License

This project is licensed under either of

 * Apache License, Version 2.0, ([LICENSE-APACHE](LICENSE-APACHE) or
   http://www.apache.org/licenses/LICENSE-2.0)
 * MIT license ([LICENSE-MIT](LICENSE-MIT) or
   http://opensource.org/licenses/MIT)

at your option.

## Contribution

Unless you explicitly state otherwise, any contribution intentionally submitted
for inclusion in `jemallocatooor-global` by you, as defined in the Apache-2.0 license,
shall be dual licensed as above, without any additional terms or conditions.

[travis]: https://travis-ci.com/jemallocatooor/jemallocatooor
[Travis-CI Status]: https://travis-ci.com/jemallocatooor/jemallocatooor.svg?branch=master
[Latest Version]: https://img.shields.io/crates/v/jemallocatooor.svg
[crates.io]: https://crates.io/crates/jemallocatooor
[docs]: https://docs.rs/jemallocatooor/badge.svg
[docs.rs]: https://docs.rs/jemallocatooor/
