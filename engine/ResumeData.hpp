#pragma once
#include <string>
#include <vector>

struct Project {
    std::string title;
    std::vector<std::string> bullets;
};

struct Education {
    std::string degree;
    std::string institution;
    std::string batch;
};

struct Certification {
    std::string name;
    std::string description;
};

struct Experience{
    std::string company;
    std::string description;
};

struct ResumeData {
    std::string name;
    std::string title;
    std::string email;
    std::string phone;

    std::string portfolio_link;
    std::string linkedin_link;
    std::string github_link;
    std::string additional_link;

    std::string summary;

    std::vector<std::string> skills;
    std::vector<std::string> tools;
    std::vector<Experience> experience;
    std::vector<Project> projects;
    std::vector<Education> education;
    std::vector<Certification> certifications;
};
