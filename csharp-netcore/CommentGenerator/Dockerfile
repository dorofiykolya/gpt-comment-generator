FROM mcr.microsoft.com/dotnet/runtime:6.0 AS base
WORKDIR /app

FROM mcr.microsoft.com/dotnet/sdk:6.0 AS build
WORKDIR /src
COPY ["CommentGenerator/CommentGenerator.csproj", "CommentGenerator/"]
RUN dotnet restore "CommentGenerator/CommentGenerator.csproj"
COPY . .
WORKDIR "/src/CommentGenerator"
RUN dotnet build "CommentGenerator.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "CommentGenerator.csproj" -c Release -o /app/publish /p:UseAppHost=false

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "CommentGenerator.dll"]
