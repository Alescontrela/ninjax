import functools

import jax as jax
import jax.numpy as jnp
import ninjax as nj


class TestJit:

  def test_plain_jit(self):
    nj.reset()
    fun = jax.jit(nj.pure(lambda: jnp.array(42)))
    assert fun({}, jax.random.PRNGKey(0))[0] == 42
    assert fun({}, jax.random.PRNGKey(0))[0] == 42

  def test_ninjax_jit(self):
    nj.reset()
    fun = nj.jit(nj.pure(lambda: jnp.array(42)))
    assert not fun.created
    assert fun({}, jax.random.PRNGKey(0))[0] == 42
    assert fun.created
    assert fun({}, jax.random.PRNGKey(0))[0] == 42
    assert fun.created

  def test_variables(self):
    nj.reset()
    v = nj.Variable(jnp.ones, (), jnp.int32)
    read = nj.jit(nj.pure(v.read))
    write = nj.jit(nj.pure(v.write))
    state = {}
    rng = jax.random.PRNGKey(0)
    _, state = read(state, rng)
    assert state == {'/Variable/value': 1}
    _, state = write(state, rng, 42)
    assert nj.pure(v.read)(state, rng)[0] == 42
    assert state == {'/Variable/value': 42}

  def test_static_args(self):
    nj.reset()
    def program(x, mode='train'):
      if mode == 'train':
        return x
      else:
        return 2 * x
    fun = nj.jit(nj.pure(program), static=['mode'])
    rng = jax.random.PRNGKey(0)
    assert fun({}, rng, jnp.array(1), mode='train')[0] == 1
    assert fun({}, rng, jnp.array(1), mode='train')[0] == 1
    assert fun({}, rng, jnp.array(1), mode='eval')[0] == 2
    assert fun({}, rng, jnp.array(1), mode='eval')[0] == 2
