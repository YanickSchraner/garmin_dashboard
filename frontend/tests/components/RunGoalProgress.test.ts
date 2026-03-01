import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import RunGoalProgress from '../../app/components/RunGoalProgress.vue'

describe('RunGoalProgress', () => {
  it('renders correctly with default props', () => {
    const wrapper = mount(RunGoalProgress)
    expect(wrapper.text()).toContain('ANNUAL GOAL')
    expect(wrapper.text()).toContain('104')
  })

  it('displays correct status text when ahead', () => {
    const wrapper = mount(RunGoalProgress, {
      props: {
        actual: 20,
        targetToDate: 15,
        status: 'ahead'
      }
    })
    expect(wrapper.text()).toContain('AHEAD')
  })

  it('displays correct status text when behind', () => {
    const wrapper = mount(RunGoalProgress, {
      props: {
        actual: 10,
        targetToDate: 15,
        status: 'behind'
      }
    })
    expect(wrapper.text()).toContain('BEHIND')
  })

  it('emits refresh event when Sync button is clicked', async () => {
    const wrapper = mount(RunGoalProgress)
    const button = wrapper.find('button')
    await button.trigger('click')
    expect(wrapper.emitted()).toHaveProperty('refresh')
  })
})
