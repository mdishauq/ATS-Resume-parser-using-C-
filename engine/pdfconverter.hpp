#ifndef PDFCONVERTER_HPP
#define PDFCONVERTER_HPP

#include <string>

class PdfConverter {
public:
    enum class Mode {
        ATS,
        VISUAL
    };

    static void set_mode(Mode m);

    static void convert_txt_to_pdf(
        const std::string& txt_path,
        const std::string& pdf_path
    );

private:
    static Mode mode;
};

#endif
