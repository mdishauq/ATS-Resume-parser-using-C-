#include "resumerenderer.hpp"
#include <cctype>

ResumeRenderer::ResumeRenderer(const ResumeData& data,
                               int max_lines_per_page)
    : resume(data),
      max_lines(max_lines_per_page),
      current_line(0),
      current_page(1)
{
}

void ResumeRenderer::new_page() {
    //out << "\n----- PAGE " << current_page + 1 << " -----\n\n";
    current_page++;
    current_line = 0;
}

void ResumeRenderer::write_line(const std::string& line) {
    if (current_line >= max_lines) {
        new_page();
    }
    out << line << '\n';
    current_line++;
}

void ResumeRenderer::write_section_header(const std::string& title) {

    if (current_line > 0) {
        write_line("");
    }

    std::string upper = title;
    for (char& c : upper) {
        c = std::toupper(static_cast<unsigned char>(c));
    }

    write_line(upper);
}


/* ---------- SECTIONS ---------- */

void ResumeRenderer::render_header() {

    // NAME in ALL CAPS
    std::string upper_name = resume.name;
    for (char& c : upper_name) {
        c = std::toupper(static_cast<unsigned char>(c));
    }
    write_line(upper_name);

    // OPTIONAL ROLE / TITLE (printed only if present)
    if (!resume.title.empty()) {
        write_line(resume.title);
    }

    write_line(resume.email + " | " + resume.phone);

    if (!resume.linkedin_link.empty())
        write_line("LinkedIn: " + resume.linkedin_link);

    if (!resume.github_link.empty())
        write_line("GitHub: " + resume.github_link);

    if (!resume.portfolio_link.empty())
        write_line("Portfolio: " + resume.portfolio_link);

    if (!resume.additional_link.empty())
        write_line(resume.additional_link);
}

void ResumeRenderer::render_summary() {
    write_section_header("Summary");
    write_line(resume.summary);
}

void ResumeRenderer::render_education() {
    write_section_header("Education");

    for (size_t i = 0; i < resume.education.size(); ++i) {
        const auto& edu = resume.education[i];
        write_line(edu.degree);
        write_line(edu.institution);
        write_line("Batch: " + edu.batch);

        if (i + 1 < resume.education.size()) {
            write_line("");
        }
    }
}

void ResumeRenderer::render_experience() {
    if (resume.experience.empty())
        return;

    write_section_header("Experience");

    for (size_t i = 0; i < resume.experience.size(); ++i) {
        const auto& exp = resume.experience[i];
        write_line(exp.company);
        write_line("- " + exp.description);

        if (i + 1 < resume.experience.size()) {
            write_line("");
        }
    }
}

void ResumeRenderer::render_projects() {
    write_section_header("Projects");

    for (size_t i = 0; i < resume.projects.size(); ++i) {
        const auto& project = resume.projects[i];
        write_line(project.title);

        for (const auto& bullet : project.bullets) {
            write_line("- " + bullet);
        }

        if (i + 1 < resume.projects.size()) {
            write_line("");
        }
    }
}

void ResumeRenderer::render_skills_and_tools() {
    write_section_header("Skills & Tools");

    for (const auto& skill : resume.skills) {
        write_line("- " + skill);
    }

    for (const auto& tool : resume.tools) {
        write_line("- " + tool);
    }
}

void ResumeRenderer::render_certifications() {
    write_section_header("Certifications");

    for (size_t i = 0; i < resume.certifications.size(); ++i) {
        const auto& cert = resume.certifications[i];

        write_line(cert.name);
        write_line("- " + cert.description);

        if (i + 1 < resume.certifications.size()) {
            write_line("");
        }
    }
}

/* ---------- FINAL ORDER ---------- */

void ResumeRenderer::render_to_file(const std::string& output_path) {
    out.open(output_path);
    if (!out.is_open()) {
        throw std::runtime_error("Failed to open output file");
    }

    current_line = 0;
    current_page = 1;

    render_header();
    render_summary();
    render_education();
    render_experience();
    render_projects();
    render_skills_and_tools();
    render_certifications();

    out.close();
}

int ResumeRenderer::get_page_count() const {
    return current_page;
}
