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
    }
  }
}

// Type exports for convenience
export type NetworkInterfaceEthernet = paths['/api/system/networks/ethernets']['get']['responses']['200']['content']['application/json'][number]
export type NetworkInterfaceBridge = paths['/api/system/networks/bridges']['get']['responses']['200']['content']['application/json'][number]
