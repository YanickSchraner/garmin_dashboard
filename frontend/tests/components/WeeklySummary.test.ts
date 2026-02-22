import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import WeeklySummary from '../../components/WeeklySummary.vue'

describe('WeeklySummary', () => {
  it('renders correctly', () => {
    const wrapper = mount(WeeklySummary)
    expect(wrapper.text()).toContain('Weekly Performance')
    expect(wrapper.text()).toContain('Sleep Quality')
    expect(wrapper.text()).toContain('Avg RHR')
    expect(wrapper.text()).toContain('Trainings')
    expect(wrapper.text()).toContain('Total Dist')
  })

  it('displays default weekly values', () => {
    const wrapper = mount(WeeklySummary)
    expect(wrapper.text()).toContain('7h 45m')
    expect(wrapper.text()).toContain('52 bpm')
  })
})
