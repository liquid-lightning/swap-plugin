# swap-plugin

`assetswap-plugin` is a Core Lightning plugin that pays an invoice which
requires a different asset than the payer holds, by routing through a
swap-provider node. The swap is two hash-linked payments and needs no change
to CLN's core.

> **Status: MVP, not production ready.** This is open-source code for
> testnets. It has not been audited and must not be used with funds that
> matter.

## How it works

1. The payee wraps an invoice and the asset it requires into one string with
   `assetinvoice`.
2. The payer runs `payassetinvoice`. It first tries a direct payment in the
   same asset. If that is not possible it prices a swap from its own local
   pricing plugin and sends leg 1 to a swap provider, with the payee's invoice
   packed into the payment's metadata. Leg 1 uses the payee's payment hash.
3. The provider's `htlc_accepted` hook decodes the metadata and prices the swap
   at its current price. If it is profitable, the provider pays the payee's
   invoice (leg 2) and settles leg 1 with the preimage it gets back. If it is
   not, it fails leg 1.

There is no pre-negotiated quote and no direct connection between payer and
provider: leg 1 is routed like any other payment.

Pricing is not this plugin's job. It calls the `pricetiers` RPC method of the
[pricer plugin](https://github.com/liquid-lightning/pricer-plugin), which must
run on the same node.

## Build

```
cargo build --release
```

The binary is `target/release/assetswap-plugin`. Rust 1.85 or later is needed.
`Cargo.toml` shows how to build against a CLN checkout's crates instead of the
published ones.

## Run

```
lightningd --plugin=/path/to/assetswap-plugin \
    --plugin=/path/to/pricetiers-plugin \
    --assetswap-provider=<provider node id>
```

| Option | Default | Meaning |
|---|---|---|
| `assetswap-provider` | none | Node id of a swap provider to send leg 1 to when an invoice cannot be paid directly. Repeatable; only the first is used. |
| `assetswap-remote` | none | `asset:rpc-file`. A provider pays leg 2 in this asset from another node of its own, on another chain. Repeatable, one per asset. |
| `assetswap-cltv-safety-blocks` | 18 | CLTV blocks a provider keeps as margin on leg 1 over leg 2's final CLTV. |
| `assetswap-min-hop-budget` | 34 | Up-front CLTV budget check before leg 2 is attempted. |
| `assetswap-block-seconds` | discovered | `asset:seconds`. Block time of the chain an asset is paid on. Leg 1's and leg 2's CLTVs are compared by time, not block count. Repeatable, one per asset. |
| `assetswap-leg2-maxfee-ppm` | 5000 | Routing fee a provider allows leg 2, in parts per million of its amount. |
| `assetswap-leg2-maxfee-base-msat` | 5000 | Fixed part of the routing fee a provider allows leg 2, in msat of leg 2's asset. |

## RPC

| Method | What it does |
|---|---|
| `assetinvoice` | Creates an invoice and packages it with the asset it requires into one string |
| `quoteassetinvoice` | Estimates what paying such a string would cost, from this node's own pricing plugin, without paying |
| `payassetinvoice` | Pays such a string, through a swap provider if the payer does not hold the asset |

## Tests

`cargo test` runs the unit tests.

The integration tests in `tests/` use Core Lightning's `pyln-testing` fixtures
and need a checkout of the CLN fork. Point `LIGHTNING_SRC` at it, or
`CLN_TESTS_DIR` at its `tests/` directory. The
[developer edition](https://github.com/liquid-lightning) runs them with
`./dev test swap`.

## Related repositories

- [Core Lightning fork](https://github.com/MarkCherepovskyi/lightning) with the asset-channel core changes
- [liquid-plugin](https://github.com/liquid-lightning/liquid-plugin), the Liquid asset-channel plugin
- [evm-plugin](https://github.com/liquid-lightning/evm-plugin), the EVM backend plugin
- [pricer-plugin](https://github.com/liquid-lightning/pricer-plugin), the pricing policy this plugin calls

## Licence

MIT, see [LICENSE](LICENSE).
