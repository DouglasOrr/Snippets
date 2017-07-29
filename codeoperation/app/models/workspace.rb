# Provides simple 'file-related' services
class CodeopFile
  attr_reader :path
  def initialize path
    @path = path
  end
  def name
    File.basename path
  end
end

# Provides simple 'workspace-related' services
class Workspace
  attr_reader :path
  def initialize path
    @path = path
  end
  def name
    File.basename path
  end
  def files
    Dir["#{path}/*"].map {|p| CodeopFile.new p}
  end
  def [] name
    CodeopFile.new "#{path}/#{name}"
  end
end

# Provides a single-level root for a collection of workspaces
class WorkspaceRoot
  attr_reader :path
  def initialize path
    @path = path
  end
  def workspaces
    Dir["#{path}/*"].map {|p| Workspace.new p}
  end
  def [] name
    Workspace.new "#{path}/#{name}"
  end
end
