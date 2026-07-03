IF DB_ID(N'gzdouban') IS NULL
BEGIN
    CREATE DATABASE gzdouban;
END
GO

USE gzdouban;
GO

IF OBJECT_ID(N'dbo.movies', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.movies (
        id INT IDENTITY(1,1) PRIMARY KEY,
        directors NVARCHAR(255),
        rate NVARCHAR(255),
        title NVARCHAR(255),
        casts NVARCHAR(255),
        cover NVARCHAR(255),
        [year] NVARCHAR(255),
        types NVARCHAR(255),
        country NVARCHAR(255),
        lang NVARCHAR(255),
        [time] NVARCHAR(255),
        movieTime NVARCHAR(255),
        commentLen NVARCHAR(255),
        star NVARCHAR(255),
        summary NVARCHAR(2555),
        imgList NVARCHAR(2555),
        detailLink NVARCHAR(2555)
    );
END
GO
