# A synchronized chat distributor, currently residing purely in memory
class ChatStream
  # Create a new, empty, stream
  def initialize
    @chat = []
    @listeners = {}
  end
  # Send a message to listeners, and wake them up if they're sleeping
  def send message
    Thread.exclusive do
      @chat << message
      @listeners.each {|t,n| t.wakeup}
    end
  end
  # Register for future messages, and retrieve a copy of existing messages
  # when additional messages arrive, the calling thread will be 'woken' by
  # <code>Thread#wakeup</code>
  def register thread
    Thread.exclusive do
      @listeners[thread] = @chat.size
      Array.new(@chat)
    end
  end
  # Retrieve unread messages for the calling thread, and clear the inbox
  def messages thread
    Thread.exclusive do
      n = @listeners[thread]
      @listeners[thread] = @chat.size
      @chat.drop(n)
    end
  end
  # Retrieve messages in a loop, yielding a message each time one arrives
  def receive
    (self.register Thread.current).each {|m| yield m}
    while true do
      Thread.stop
      (self.messages Thread.current).each {|m| yield m}
    end
  end
end

