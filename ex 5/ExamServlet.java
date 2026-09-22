package exam;

import java.io.IOException;
import java.io.PrintWriter;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

@WebServlet("/ExamServlet")
public class ExamServlet extends HttpServlet {

    @Override
    protected void doPost(HttpServletRequest request,
                           HttpServletResponse response)
            throws ServletException, IOException {

        // Get student name
        String username = request.getParameter("username");

        // Get student answers
        String q1 = request.getParameter("q1");
        String q2 = request.getParameter("q2");
        String q3 = request.getParameter("q3");
        String q4 = request.getParameter("q4");
        String q5 = request.getParameter("q5");
        String q6 = request.getParameter("q6");
        String q7 = request.getParameter("q7");
        String q8 = request.getParameter("q8");
        String q9 = request.getParameter("q9");
        String q10 = request.getParameter("q10");
        String q11 = request.getParameter("q11");
        String q12 = request.getParameter("q12");

        // Correct answers
        String[] correctAnswers = {
            "p",
            "color",
            "a",
            "img",
            "background-color",
            "h1",
            "font-size",
            "ul",
            "font-weight",
            "br",
            "text-align",
            "table"
        };

        // Student answers
        String[] studentAnswers = {
            q1, q2, q3, q4, q5, q6,
            q7, q8, q9, q10, q11, q12
        };

        // Calculate marks
        int marks = 0;

        for (int i = 0; i < 12; i++) {

            if (correctAnswers[i].equals(studentAnswers[i])) {
                marks++;
            }
        }

        // Calculate percentage
        double percentage = (marks / 12.0) * 100;

        // Pass or fail
        String result;

        if (marks >= 6) {
            result = "PASS";
        } else {
            result = "FAIL";
        }

        // Display result
        response.setContentType("text/html;charset=UTF-8");

        PrintWriter out = response.getWriter();

        out.println("<!DOCTYPE html>");
        out.println("<html>");
        out.println("<head>");
        out.println("<title>Exam Result</title>");

        out.println("<style>");

        out.println("body {");
        out.println("font-family: Arial;");
        out.println("background-color: lightblue;");
        out.println("margin: 0;");
        out.println("text-align: center;");
        out.println("}");

        out.println("h1 {");
        out.println("background-color: darkblue;");
        out.println("color: white;");
        out.println("padding: 20px;");
        out.println("margin: 0;");
        out.println("}");

        out.println(".result-box {");
        out.println("width: 500px;");
        out.println("margin: 50px auto;");
        out.println("padding: 30px;");
        out.println("background-color: white;");
        out.println("border: 1px solid gray;");
        out.println("}");

        out.println(".marks {");
        out.println("font-size: 30px;");
        out.println("font-weight: bold;");
        out.println("color: darkblue;");
        out.println("}");

        out.println(".pass {");
        out.println("color: green;");
        out.println("font-size: 25px;");
        out.println("font-weight: bold;");
        out.println("}");

        out.println(".fail {");
        out.println("color: red;");
        out.println("font-size: 25px;");
        out.println("font-weight: bold;");
        out.println("}");

        out.println("</style>");
        out.println("</head>");

        out.println("<body>");

        out.println("<h1>HTML & CSS Online Examination</h1>");

        out.println("<div class='result-box'>");

        out.println("<h2>Exam Result</h2>");

        out.println("<p>Student Name: <b>" + username + "</b></p>");

        out.println("<p class='marks'>Marks: "
                + marks + " / 12</p>");

        out.println("<p>Percentage: "
                + String.format("%.2f", percentage)
                + "%</p>");

        if (marks >= 6) {
            out.println("<p class='pass'>Result: PASS</p>");
        } else {
            out.println("<p class='fail'>Result: FAIL</p>");
        }

        out.println("</div>");

        out.println("</body>");
        out.println("</html>");
    }
}
