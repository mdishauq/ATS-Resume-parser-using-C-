#pragma once
#include "json.hpp"
#include "ResumeData.hpp"

using json = nlohmann::json;

class ResumeParser{
public:
    ResumeParser(const std::string &json_text);

    ResumeData parse();

private:
    json parsed_json;

};