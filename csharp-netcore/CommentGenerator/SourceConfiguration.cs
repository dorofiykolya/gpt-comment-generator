namespace CommentGenerator;

[Serializable]
public class SourceConfiguration
{
    public string? Root { get; set; }
    public string[] Dirs { get; set; }
    public string ApiKey { get; set; }
}
