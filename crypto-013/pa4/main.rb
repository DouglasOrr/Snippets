require 'net/http'

# general helpers

def from_hex str
  str.scan(/../).map(&:hex)
end
def to_hex arr
  arr.map {|x| "%02x" % x}.join
end

def query ciphertext
  uri = URI.parse("http://crypto-class.appspot.com/po?er=#{to_hex ciphertext}")
  {'200' => :success,
    '403' => :bad_pad,
    '404' => :bad_mac}[Net::HTTP.get_response(uri).code]
end

# specific stuff

ALPHABET_ASCFREQ = "eitsanhurdmwgvlfbkopjxczyq"
COMMON_CHARS = [' '] + ALPHABET_ASCFREQ.chars + ALPHABET_ASCFREQ.upcase.chars + ('0'..'9').to_a
ASCII_BYTES = (COMMON_CHARS.map(&:ord) + (0..255).to_a).uniq!

# break the given block, and return the plaintext
def oracle prev, block
  raise "Bad block length" unless (block.length == 16)

  message = ""
  prev_xor_message = Array.new(prev)
  is_last_block = (query(prev + block) == :success)
  last_block_pad = nil

  (1..16).each do |pad|
    next if last_block_pad and pad <= last_block_pad

    # make a working copy of the padded prev
    prev_copy = Array.new(prev_xor_message)
    (-1.downto(1-pad)).each do |i|
      prev_copy[i] = prev_xor_message[i] ^ pad
    end

    # search for the plaintext
    plain = ASCII_BYTES.find do |guess|
      prev_copy[-pad] = prev[-pad] ^ guess ^ pad
      query(prev_copy + block) == :bad_mac
    end

    # update the state of what we know
    if plain == nil
      raise "Failed to decode block"
    elsif is_last_block and pad == 1
      last_block_pad = plain
      (1..plain).each {|p| prev_xor_message[-p] = prev[-p] ^ plain}
      STDERR.print "[pad=#{plain}]\n"
    else
      prev_xor_message[-pad] = prev[-pad] ^ plain
      message.prepend(plain.chr)
      STDERR.print "\r#{message}"
    end
  end
  STDERR.print "\n"

  message
end

def decode ciphertext
  plain_blocks = (16...ciphertext.length).step(16).map do |index|
    oracle(ciphertext[0...index], ciphertext[index...(index+16)])
  end.join
end

# script

ciphertext = from_hex "f20bdba6ff29eed7b046d1df9fb7000058b1ffb4210a580f748b4ac714c001bd4a61044426fb515dad3f21f18aa577c0bdf302936266926ff37dbf7035d5eeb4"
p decode ciphertext
