const memoryLocalStorage = new Map()
const memorySessionStorage = new Map()

function resolveStorage (type) {
  if (typeof window === 'undefined') return null
  try {
    return type === 'local' ? window.localStorage : window.sessionStorage
  } catch (error) {
    return null
  }
}

function safeGet (type, memoryStore, key, fallback = '') {
  const storage = resolveStorage(type)
  if (storage) {
    try {
      const value = storage.getItem(key)
      if (value !== null) return value
    } catch (error) {
      // ignore and fallback to memory store
    }
  }
  return memoryStore.has(key) ? memoryStore.get(key) : fallback
}

function safeSet (type, memoryStore, key, value) {
  const normalized = value == null ? '' : String(value)
  memoryStore.set(key, normalized)

  const storage = resolveStorage(type)
  if (!storage) return false

  try {
    storage.setItem(key, normalized)
    return true
  } catch (error) {
    return false
  }
}

function safeRemove (type, memoryStore, key) {
  memoryStore.delete(key)

  const storage = resolveStorage(type)
  if (!storage) return false

  try {
    storage.removeItem(key)
    return true
  } catch (error) {
    return false
  }
}

export function safeLocalGet (key, fallback = '') {
  return safeGet('local', memoryLocalStorage, key, fallback)
}

export function safeLocalSet (key, value) {
  return safeSet('local', memoryLocalStorage, key, value)
}

export function safeLocalRemove (key) {
  return safeRemove('local', memoryLocalStorage, key)
}

export function safeSessionGet (key, fallback = '') {
  return safeGet('session', memorySessionStorage, key, fallback)
}

export function safeSessionSet (key, value) {
  return safeSet('session', memorySessionStorage, key, value)
}

export function safeSessionRemove (key) {
  return safeRemove('session', memorySessionStorage, key)
}
