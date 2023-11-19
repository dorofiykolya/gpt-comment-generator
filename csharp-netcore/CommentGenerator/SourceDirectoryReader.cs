namespace CommentGenerator;

public class SourceDirectoryReader
{
    public string[] GetFiles(string[] directories)
    {
        return directories.SelectMany(GetFiles).ToArray();
    }

    public string[] GetFiles(string directory)
    {
        return Directory.GetFiles(directory, "*.cs", SearchOption.AllDirectories);
    }
}
