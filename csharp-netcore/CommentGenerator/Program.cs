using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using System.Collections.Generic;
using System.Text;
using Newtonsoft.Json;
using OpenAI;
using OpenAI.Managers;
using OpenAI.ObjectModels;
using OpenAI.ObjectModels.RequestModels;

namespace CommentGenerator
{
    class Program
    {
        static void Main(string[] args)
        {
            var configuration = JsonConvert.DeserializeObject<SourceConfiguration>(File.ReadAllText("appsettings.json"));
            var dirs = configuration.Dirs
                    .Select(s =>
                            string.IsNullOrWhiteSpace(configuration.Root)
                                    ? s
                                    : Path.Combine(configuration.Root, s.Trim())
                    )
                    .ToArray();

            var reader = new SourceDirectoryReader();
            var files = reader.GetFiles(dirs);
            var codeBuilder = new StringBuilder();
            foreach (var file in files)
            {
                var fileCode = File.ReadAllText(file);
                codeBuilder.AppendLine("// BEGIN: " + file);
                codeBuilder.AppendLine(fileCode);
                codeBuilder.AppendLine("// END: " + file);
                codeBuilder.AppendLine();
            }
            var code = codeBuilder.ToString();
            var tree = CSharpSyntaxTree.ParseText(code);
            var tokens = OpenAI.Tokenizer.GPT3.TokenizerGpt3.TokenCount(code);
            var classes = tree.GetRoot().DescendantNodes().OfType<ClassDeclarationSyntax>().ToArray();
            var interfaces = tree.GetRoot().DescendantNodes().OfType<InterfaceDeclarationSyntax>().ToArray();
            var structures = tree.GetRoot().DescendantNodes().OfType<StructDeclarationSyntax>().ToArray();

            Console.WriteLine($"TOKENS: {tokens}");
            Console.WriteLine($"CLASSES: {classes.Length} [ {string.Join(',', classes.Select(s => s.Identifier.ValueText))} ] ]");
            Console.WriteLine($"INTERFACES: {interfaces.Length} [ {string.Join(',', interfaces.Select(s => s.Identifier.ValueText))} ]");
            Console.WriteLine($"STRUCTURES: {structures.Length} [ {string.Join(',', structures.Select(s => s.Identifier.ValueText))} ]");

            var openAi = new OpenAIService(new OpenAiOptions
            {
                ApiKey = configuration.ApiKey
            });
            var openAiCompletion = openAi.ChatCompletion.CreateCompletion(
                    chatCompletionCreate: new ChatCompletionCreateRequest
                    {
                        Temperature = 0f,
                        Model = Models.Gpt_4_1106_preview,
                        ResponseFormat = new ResponseFormat
                        {
                            Type = "json_object"
                        },
                        Messages = new List<ChatMessage>
                        {
                            new ChatMessage(
                                    role: StaticValues.ChatMessageRoles.System,
                                    content:
                                    @"You are a comment and documentation generator for different types of programming code.
You will be provided a concatenated code from all project's source files.
You must analyze each given class, interface, structure, delegate, methods, fields, properties and define relationships between them.
Based on analyzed info, you must create comments that suits programming language of the given class, method or etc.
You must strictly follow general comment and documentation rules for given programming language C#.
Remember to indicate method or class main purpose and variables in your comments.
Write comments ONLY as JSON."
                            ),
                            new ChatMessage(
                                    role: StaticValues.ChatMessageRoles.User,
                                    content: code
                            )
                        }
                    },
                    modelId: Models.Gpt_4_1106_preview
            );
            foreach (var choice in openAiCompletion.Result.Choices)
            {
                Console.WriteLine(choice.Message.Content);
            }
        }
    }
}
