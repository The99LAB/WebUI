import { client } from '../boot/api'
import type { paths } from '../types/api'

export function useApi() {
  return {
    // Network Manager endpoints
    networks: {
      async getEthernets() {
        const { data, error } = await client.GET('/api/system/networks/ethernets')
        if (error) throw error
        return data
      },

      async getEthernet(ethernetId: string) {
        const { data, error } = await client.GET('/api/system/networks/ethernets/{ethernet_id}', {
          params: { path: { ethernet_id: ethernetId } }
        })
        if (error) throw error
        return data
      },

      async getBridges() {
        const { data, error } = await client.GET('/api/system/networks/bridges')
        if (error) throw error
        return data
      },

      async getBridge(bridgeId: string) {
        const { data, error } = await client.GET('/api/system/networks/bridges/{bridge_id}', {
          params: { path: { bridge_id: bridgeId } }
        })
        if (error) throw error
        return data
      },

      async updateEthernet(iface: paths['/api/system/networks/ethernets']['put']['requestBody']['content']['application/json']) {
        const { data, error } = await client.PUT('/api/system/networks/ethernets', {
          body: iface
        })
        if (error) throw error
        return data
      },

      async updateBridge(iface: paths['/api/system/networks/bridges']['put']['requestBody']['content']['application/json']) {
        const { data, error } = await client.PUT('/api/system/networks/bridges', {
          body: iface
        })
        if (error) throw error
        return data
      },

      async apply() {
        const { data, error } = await client.POST('/api/system/networks/apply')
        if (error) throw error
        return data
      }
    },

    // VM Manager endpoints
    vm: {
      async getAll() {
        const { data, error } = await client.GET('/api/vm/')
        if (error) throw error
        return data
      },

      async get(vmId: number) {
        const { data, error } = await client.GET('/api/vm/{vm_id}', {
          params: { path: { vm_id: vmId } }
        })
        if (error) throw error
        return data
      },

      async update(vmId: number, vm: paths['/api/vm/{vm_id}']['put']['requestBody']['content']['application/json']) {
        const { data, error } = await client.PUT('/api/vm/{vm_id}', {
          params: { path: { vm_id: vmId } },
          body: vm
        })
        if (error) throw error
        return data
      },

      async delete(vmId: number) {
        const { data, error } = await client.DELETE('/api/vm/{vm_id}', {
          params: { path: { vm_id: vmId } }
        })
        if (error) throw error
        return data
      },

      async start(vmId: number) {
        const { data, error } = await client.POST('/api/vm/{vm_id}/start', {
          params: { path: { vm_id: vmId } }
        })
        if (error) throw error
        return data
      },

      async shutdown(vmId: number) {
        const { data, error } = await client.POST('/api/vm/{vm_id}/shutdown', {
          params: { path: { vm_id: vmId } }
        })
        if (error) throw error
        return data
      },

      async forcestop(vmId: number) {
        const { data, error } = await client.POST('/api/vm/{vm_id}/forcestop', {
          params: { path: { vm_id: vmId } }
        })
        if (error) throw error
        return data
      },

      async reset(vmId: number) {
        const { data, error } = await client.POST('/api/vm/{vm_id}/reset', {
          params: { path: { vm_id: vmId } }
        })
        if (error) throw error
        return data
      },

      async getTemplatesBasic() {
        const { data, error } = await client.GET('/api/vm/templates/basic')
        if (error) throw error
        return data
      },

      async getTemplateBasic(templateId: number) {
        const { data, error } = await client.GET('/api/vm/templates/basic/{template_id}', {
          params: { path: { template_id: templateId } }
        })
        if (error) throw error
        return data
      },

      async getXmlTemplates() {
        const { data, error } = await client.GET('/api/vm/templates/xml')
        if (error) throw error
        return data
      },

      async getXmlTemplate(xmlTemplateId: number) {
        const { data, error } = await client.GET('/api/vm/templates/xml/{xml_template_id}', {
          params: { path: { xml_template_id: xmlTemplateId } }
        })
        if (error) throw error
        return data
      },

      async getBridgeNetworks() {
        const { data, error } = await client.GET('/api/vm/network/bridge')
        if (error) throw error
        return data
      },

      async createBridgeNetwork(bridge: any) {
        const { data, error } = await client.POST('/api/vm/network/bridge', {
          body: bridge
        })
        if (error) throw error
        return data
      },

      async getBridgeNetwork(bridgeId: number) {
        const { data, error } = await client.GET('/api/vm/network/bridge/{bridge_id}', {
          params: { path: { bridge_id: bridgeId } }
        })
        if (error) throw error
        return data
      },

      async deleteBridgeNetwork(bridgeId: number) {
        const { data, error } = await client.DELETE('/api/vm/network/bridge/{bridge_id}', {
          params: { path: { bridge_id: bridgeId } }
        })
        if (error) throw error
        return data
      },

      async updateBridgeNetwork(bridgeId: number, bridge: paths['/api/vm/network/bridge/{bridge_id}']['put']['requestBody']['content']['application/json']) {
        const { data, error } = await client.PUT('/api/vm/network/bridge/{bridge_id}', {
          params: { path: { bridge_id: bridgeId } },
          body: bridge
        })
        if (error) throw error
        return data
      },

      async applyBridgeNetworks() {
        const { data, error } = await client.POST('/api/vm/network/bridge/apply')
        if (error) throw error
        return data
      },

      async getCustomNetworks() {
        const { data, error } = await client.GET('/api/vm/network/custom')
        if (error) throw error
        return data
      },

      async createCustomNetwork(custom: any) {
        const { data, error } = await client.POST('/api/vm/network/custom', {
          body: custom
        })
        if (error) throw error
        return data
      },

      async getCustomNetwork(customId: number) {
        const { data, error } = await client.GET('/api/vm/network/custom/{custom_id}', {
          params: { path: { custom_id: customId } }
        })
        if (error) throw error
        return data
      },

      async deleteCustomNetwork(customId: number) {
        const { data, error } = await client.DELETE('/api/vm/network/custom/{custom_id}', {
          params: { path: { custom_id: customId } }
        })
        if (error) throw error
        return data
      },

      async updateCustomNetwork(customId: number, custom: paths['/api/vm/network/custom/{custom_id}']['put']['requestBody']['content']['application/json']) {
        const { data, error } = await client.PUT('/api/vm/network/custom/{custom_id}', {
          params: { path: { custom_id: customId } },
          body: custom
        })
        if (error) throw error
        return data
      }
    }
  }
}

// Type exports for convenience
export type NetworkInterfaceEthernet = paths['/api/system/networks/ethernets']['get']['responses']['200']['content']['application/json'][number]
export type NetworkInterfaceBridge = paths['/api/system/networks/bridges']['get']['responses']['200']['content']['application/json'][number]
export type VirtualMachine = paths['/api/vm/']['get']['responses']['200']['content']['application/json'][number]
export type VirtualMachineTemplate = paths['/api/vm/templates']['get']['responses']['200']['content']['application/json'][number]
export type VirtualMachineXmlTemplate = paths['/api/vm/xml_templates']['get']['responses']['200']['content']['application/json'][number]
