#include <iostream>
#include <fstream>
#include <string>
#include <stdexcept>
#include <limits>
#include "jsonparser.hpp"
#include "resumerenderer.hpp"
#include "pdfconverter.hpp"

std::string read_file(const std::string& path);

int main(int argc, char* argv[]) {
    
    // Check if called from website (with command-line arguments)
    if (argc == 3) {
        // Website mode: ./resume_engine input.json output.pdf
        std::string input_json = argv[1];
        std::string output_pdf = argv[2];
        
        try {
            // Read JSON
            std::string json_text = read_file(input_json);
            
            // Parse
            ResumeParser parser(json_text);
            ResumeData resume = parser.parse();
            
            // Render text resume (temporary file)
            ResumeRenderer renderer(resume, 55);
            renderer.render_to_file("temp_resume.txt");
            
            // Convert to PDF with custom output path
            PdfConverter::convert_txt_to_pdf("temp_resume.txt", output_pdf);
            
            std::cout << "Resume rendered to " << output_pdf << std::endl;
            
            // ATS check
            if (renderer.get_page_count() > 1) {
                std::cerr << "Warning: Resume exceeds 1 page (ATS issue)" << std::endl;
            }
            
            return 0;
            
        } catch (const std::exception& e) {
            std::cerr << "Error: " << e.what() << std::endl;
            return 1;
        }
    }
    
    // Interactive mode 
    int menu = 0;
    bool exit = false;
    std::string file_name;

    while (!exit) {

        std::cout << "1. Enter the JSON file name\n";
        std::cout << "2. Exit\n";
        std::cout << "Enter the input: ";
        std::cin >> menu;
        
        if (std::cin.fail()) {
            std::cin.clear();
            std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
            std::cout << "Invalid input. Please enter 1 or 2.\n";
            continue;
        }

        switch (menu) {

            case 1: {
                try {
                    std::cout << "Enter the file name: ";
                    std::cin >> file_name;

                    // read JSON
                    std::string json_text = read_file(file_name);

                    // parse
                    ResumeParser parser(json_text);
                    ResumeData resume = parser.parse();

                    // render text resume
                    ResumeRenderer renderer(resume, 55);
                    renderer.render_to_file("resume.txt");

                    std::cout << "Resume rendered to resume.txt\n";

                    // convert to PDF (STATIC call – correct)
                    PdfConverter::convert_txt_to_pdf("resume.txt", "resume.pdf");

                    std::cout << "Resume rendered to resume.pdf\n";

                    // ATS check
                    if (renderer.get_page_count() > 1) {
                        std::cout
                            << "- ATS Warning: Resume exceeds 1 page.\n"
                            << "Please reduce descriptions or section sizes to fit a single page.\n";
                    } else {
                        std::cout << "- Resume fits within a single page (ATS friendly).\n";
                    }

                } catch (const std::exception& e) {
                    std::cerr << "Error: " << e.what() << std::endl;
                }
                break;
            }

            case 2:
                std::cout << "Menu is switching off\n";
                exit = true;
                break;

            default:
                std::cout << "Invalid option\n";
        }
    }

    return 0;
}

// helper functions

std::string read_file(const std::string& path) {
    std::ifstream file(path);
    if (!file) {
        throw std::runtime_error("Failed to open file");
    }

    return std::string(
        (std::istreambuf_iterator<char>(file)),
        std::istreambuf_iterator<char>()
    );
}