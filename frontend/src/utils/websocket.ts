import { io, Socket } from 'socket.io-client'

class WebSocketService {
  private socket: Socket | null = null

  connect(userId: string, onNotificationReceived: (notification: any) => void) {
    if (this.socket) {
      this.socket.disconnect()
    }

    const socketUrl = `${window.location.protocol}//${window.location.hostname}:5000`
    
    this.socket = io(socketUrl, {
      transports: ['websocket', 'polling']
    })

    this.socket.on('connect', () => {
      console.log('Successfully connected to WebSockets server')
      // Join user-specific room
      this.socket?.emit('join', { user_id: userId })
    })

    this.socket.on('new_notification', (data: any) => {
      console.log('Received WebSocket notification:', data)
      onNotificationReceived(data)
    })

    this.socket.on('disconnect', () => {
      console.log('Disconnected from WebSockets server')
    })
  }

  disconnect(userId: string) {
    if (this.socket) {
      this.socket.emit('leave', { user_id: userId })
      this.socket.disconnect()
      this.socket = null
    }
  }
}

export const webSocketService = new WebSocketService()
