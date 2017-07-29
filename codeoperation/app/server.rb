require 'sinatra'
require 'haml'
require_relative 'models/chat.rb'
require_relative 'models/workspace.rb'

set :server, :thin
set :public_folder, File.join(File.dirname(__FILE__), '..', 'public')
set :views, File.join(File.dirname(__FILE__), 'views')
set :haml, :format => :xhtml

workspace_root = WorkspaceRoot.new "eg-workspace"
chat_root = Hash.new {|h,k| h[k] = ChatStream.new}
def workspace_links root
  root.workspaces.map {|w| [w.name, url("/workspace/#{w.name}")]}
end
def file_links workspace
  workspace.files.map {|f| [f.name, url("/workspace/#{workspace.name}/#{f.name}")]}
end

# Workspace API
get '/' do
  haml :index, :locals => { :workspaces => workspace_links(workspace_root) }
end

get '/workspace/:workspace' do
  workspace = workspace_root[params[:workspace]]
  haml :workspace_index, :locals => { :workspace_name => workspace.name, :files => file_links(workspace) }
end

get '/workspace/:workspace/:file' do
  workspace = workspace_root[params[:workspace]]
  file = workspace[params[:file]]
  haml :editor, :locals => {
    :file_name => file.name,
    :file_path => url("/file/#{workspace.name}/#{file.name}"),
    :workspace_name => workspace.name,
    :workspace_link => url("/workspace/#{workspace.name}"),
    :home_link => url("/"),
    :chat_link => url("/chatter/#{workspace.name}"),
    :files => file_links(workspace)
  }
end

# RESTful file handling API
get '/file/:workspace/:file' do
  file = workspace_root[params[:workspace]][params[:file]]
  send_file file.path
end

# Chat API
post '/chatter/:workspace' do
  chat_root[params[:workspace]].send [params[:name].chomp, params[:text].chomp] if params[:name] and params[:text]
end

get '/chatter/:workspace' do
  stream do |out|
    chat_root[params[:workspace]].receive {|n,m| out << "[#{n}] #{m}\n"}
  end
end
