import { shallowMount, createLocalVue } from '@vue/test-utils'
import Vuex from 'vuex'
import Logout from '@/components/Logout'

const localVue = createLocalVue()
localVue.use(Vuex)

describe('Logout.vue', () => {
  let getters
  let store

  beforeEach(() => {
    getters = {
      'auth/isAuthenticated': jest.fn()
    }
    store = new Vuex.Store({
      getters
    })
  })

  it('renders properly', () => {
    const wrapper = shallowMount(Logout, { store, localVue })
    const anchor = wrapper.find('a')
    expect(anchor.text()).toBe('Logout')
  })
})
