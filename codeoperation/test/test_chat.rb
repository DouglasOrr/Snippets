require 'minitest/spec'
require 'minitest/autorun'
require './app/models/chat.rb'

describe ChatStream do
  it "can be used as a general message queue" do
    chat = ChatStream.new

    (chat.register Thread.current).must_be_empty
    your_messages = []
    you = Thread.new do
      your_messages.concat(chat.register Thread.current)
      (1..100).each do |i|
        chat.send "B #{i}"
        your_messages.concat(chat.messages Thread.current)
      end
    end
    (1..100).each {|i| chat.send "A #{i}"}
    you.join

    your_messages.concat(chat.messages you)
    my_messages = chat.messages Thread.current

    my_messages.must_equal your_messages
    (1..100).each do |i|
      my_messages.must_include "A #{i}"
      my_messages.must_include "B #{i}"
    end
  end
end

