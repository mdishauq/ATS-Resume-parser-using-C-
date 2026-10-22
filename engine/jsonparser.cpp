#include "jsonparser.hpp"
#include <stdexcept>

ResumeParser::ResumeParser(const std::string &json_text){
    parsed_json = json::parse(json_text);
}

ResumeData ResumeParser::parse(){
    ResumeData resume;

    //name
    if (!parsed_json.contains("name") || !parsed_json["name"].is_string()){
        throw std::runtime_error("name is required");
    }
    resume.name = parsed_json["name"];

    //links
    if (parsed_json.contains("title")){
        resume.portfolio_link = parsed_json["title"].get<std::string>();
    }

    //email
    if (!parsed_json.contains("email") || !parsed_json["email"].is_string()){
        throw std::runtime_error("email is required");
    }
    resume.email = parsed_json["email"].get<std::string>();

    //phone
    if (!parsed_json.contains("phone") || !parsed_json["phone"].is_string()){
        throw std::runtime_error("phone is required");
    }
    resume.phone = parsed_json["phone"].get<std::string>();

    //links
    if (parsed_json.contains("portfolio_link")){
        resume.portfolio_link = parsed_json["portfolio_link"].get<std::string>();
    }
    
    if(parsed_json.contains("github_link")){
        resume.github_link = parsed_json["github_link"].get<std::string>();
    }

    if(parsed_json.contains("linkedin_link")){
        resume.linkedin_link = parsed_json["linkedin_link"].get<std::string>();
    }

    if(parsed_json.contains("additional_link")){
        resume.additional_link = parsed_json["additional_link"].get<std::string>();
    }

    //summary
    if(!parsed_json.contains("summary") || !parsed_json["summary"].is_string()){
        throw std::runtime_error("summary must be a string!");
    }
    resume.summary = parsed_json["summary"].get<std::string>();
    
    //skills
    if(!parsed_json.contains("skills") || (!parsed_json["skills"].is_array())){
        throw std::runtime_error("skills must be array!");
    }

    for(const auto& skill : parsed_json["skills"]){
        if(!skill.is_string()){
            throw std::runtime_error("each skill must be a string!");
        }
        resume.skills.push_back(skill.get<std::string>());
    }

    //tools
    if(!parsed_json.contains("tools") || (!parsed_json["tools"].is_array())){
        throw std::runtime_error("tools must be array!");
    }

    for(const auto& tool : parsed_json["tools"]){
        if(!tool.is_string()){
            throw std::runtime_error("each tool must be a string!");
        }
        resume.tools.push_back(tool.get<std::string>());
    }

    //projects
    if(!parsed_json.contains("projects") || (!parsed_json["projects"].is_array())){
        throw std::runtime_error("projects must be array!");
    }
    for(const auto &p : parsed_json["projects"]){
        Project project;
        if(!p.contains("title") || (!p["title"].is_string())){
            throw std::runtime_error("titles must be string!");
        }
        project.title = p["title"].get<std::string>();
        if (!p.contains("bullets") || !p["bullets"].is_array()) {
            throw std::runtime_error("project bullets must be array!");
        }
        for (const auto &bul : p["bullets"]) {
            if (!bul.is_string()) {
                throw std::runtime_error("each bullet must be a string!");
            }
        project.bullets.push_back(bul.get<std::string>());
        }
        resume.projects.push_back(project);
    }

    //Education
    if(!parsed_json.contains("education") || (!parsed_json["education"].is_array())){
        throw std::runtime_error("education must be array!");
    }
    for(const auto &ed : parsed_json["education"]){
        Education education;
        education.degree = ed["degree"].get<std::string>();
        education.institution = ed["institution"].get<std::string>();
        education.batch = ed["batch"].get<std::string>();
        resume.education.push_back(education);
    }

    //Certifications
    if(!parsed_json.contains("certifications") || (!parsed_json["certifications"].is_array())){
        throw std::runtime_error("certifications must be array!");
    }
    for(const auto &cert : parsed_json["certifications"]){
        Certification certification;
        certification.name = cert["name"].get<std::string>();
        certification.description = cert["description"].get<std::string>();
        resume.certifications.push_back(certification);
    }

    if(!parsed_json.contains("experience") || (!parsed_json["experience"].is_array())){
        throw std::runtime_error("experience must be array!");
    }
    for(const auto &exp : parsed_json["experience"]){
        Experience experience;
        experience.company = exp["company"].get<std::string>();
        experience.description = exp["description"].get<std::string>();
        resume.experience.push_back(experience);
    }

    return resume;
}