#include "ResumeData.hpp"
#include <fstream>
#include <iostream>
#include <string>

class ResumeRenderer {
public:
    ResumeRenderer(const ResumeData& data, int max_lines_per_page);

    void render_to_file(const std::string& output_path);

    int get_page_count() const;

private:
    const ResumeData& resume;

    int max_lines;
    int current_line;
    int current_page;

    std::ofstream out;

    void new_page();
    void write_line(const std::string& line);
    void write_section_header(const std::string& title);

    // section renderers
    void render_header();
    void render_summary();
    void render_education();
    void render_experience();          
    void render_projects();
    void render_skills_and_tools();    
    void render_certifications();
};
