#include "pdfconverter.hpp"
#include <iostream>
#include <hpdf.h>
#include <fstream>
#include <sstream>
#include <vector>
#include <stdexcept>
#include <cctype>

static void error_handler(
    HPDF_STATUS,
    HPDF_STATUS,
    void*)
{
    throw std::runtime_error("libharu PDF error");
}

/* ---------- STRICT section header detection ---------- */
/* Header must be:
   - ALL CAPS
   - No bullet
   - No leading spaces
*/
static bool is_section_header(const std::string& line)
{
    if (line.empty()) return false;
    if (line[0] == '-' || line[0] == '*') return false;

    for (char c : line) {
        if (std::isalpha((unsigned char)c) && !std::isupper(c))
            return false;
    }
    return true;
}

/* ---------- Bullet detection ---------- */
static bool is_bullet_line(const std::string& line)
{
    return !line.empty() && (line[0] == '-' || line[0] == '*');
}

static std::string normalize_bullet(const std::string& line)
{
    if (is_bullet_line(line))
        return "- " + line.substr(1);

    return line;
}

/* ---------- Word wrapping ---------- */
static std::vector<std::string> wrap_line(
    HPDF_Page page,
    const std::string& text,
    float max_width)
{
    std::vector<std::string> lines;
    std::istringstream iss(text);
    std::string word, current;

    while (iss >> word) {
        std::string test = current.empty() ? word : current + " " + word;

        if (HPDF_Page_TextWidth(page, test.c_str()) <= max_width)
            current = test;
        else {
            if (!current.empty())
                lines.push_back(current);
            current = word;
        }
    }

    if (!current.empty())
        lines.push_back(current);

    return lines;
}

void PdfConverter::convert_txt_to_pdf(
    const std::string& txt_path,
    const std::string& pdf_path)
{
    std::ifstream in(txt_path);
    if (!in)
        throw std::runtime_error("Failed to open input text file");

    HPDF_Doc pdf = HPDF_New(error_handler, nullptr);
    HPDF_Page page = HPDF_AddPage(pdf);
    HPDF_Page_SetSize(page, HPDF_PAGE_SIZE_A4, HPDF_PAGE_PORTRAIT);

    HPDF_Font font_normal = HPDF_GetFont(pdf, "Helvetica", nullptr);
    HPDF_Font font_bold   = HPDF_GetFont(pdf, "Helvetica-Bold", nullptr);

    const float font_size = 11.0f;
    const float line_height = 14.0f;

    const float lm = 50, rm = 50, tm = 50, bm = 50;

    float pw = HPDF_Page_GetWidth(page);
    float ph = HPDF_Page_GetHeight(page);
    float usable_width = pw - lm - rm;

    float x = lm;
    float y = ph - tm;

    bool last_line_empty = true;

    std::string raw;
    while (std::getline(in, raw)) {

        /* -------- Controlled blank lines -------- */
        if (raw.empty()) {
            if (!last_line_empty) {
                y -= line_height * 0.4f;
                last_line_empty = true;
            }
            continue;
        }
        last_line_empty = false;

        bool header = is_section_header(raw);
        bool bullet = is_bullet_line(raw);

        raw = normalize_bullet(raw);

        /* -------- Section header (ONCE) -------- */
        if (header) {
            y -= line_height * 0.6f;

            HPDF_Page_SetFontAndSize(page, font_bold, font_size);
            HPDF_Page_BeginText(page);
            HPDF_Page_TextOut(page, x, y, raw.c_str());
            HPDF_Page_EndText(page);

            /* single underline only */
            HPDF_Page_MoveTo(page, x, y - 2);
            HPDF_Page_LineTo(page, pw - rm, y - 2);
            HPDF_Page_Stroke(page);

            y -= line_height;
            continue;
        }

        /* -------- Normal text (skills, tools, bullets) -------- */
        HPDF_Page_SetFontAndSize(page, font_normal, font_size);

        float text_x = bullet ? x + 12 : x;
        float wrap_width = bullet ? usable_width - 12 : usable_width;

        auto wrapped = wrap_line(page, raw, wrap_width);

        for (const auto& l : wrapped) {

            if (y < bm + line_height) {
                page = HPDF_AddPage(pdf);
                HPDF_Page_SetFontAndSize(page, font_normal, font_size);
                y = HPDF_Page_GetHeight(page) - tm;
            }

            HPDF_Page_BeginText(page);
            HPDF_Page_TextOut(page, text_x, y, l.c_str());
            HPDF_Page_EndText(page);

            y -= line_height;
        }
    }

    /* -------- Footer only if space truly exists -------- */
    if (y - bm > line_height * 3) {
        /*
        HPDF_Page_SetFontAndSize(page, font_normal, 9);
        HPDF_Page_BeginText(page);
        HPDF_Page_TextOut(
            page,
            lm,
            bm - 12,
            "Note: Additional space is available. You may add more content or download as-is."
        );
        HPDF_Page_EndText(page);
        */
       std::cout << "Additional space is available. You may add more content or download as-is." << std::endl;
        
    }

    HPDF_SaveToFile(pdf, pdf_path.c_str());
    HPDF_Free(pdf);
}
