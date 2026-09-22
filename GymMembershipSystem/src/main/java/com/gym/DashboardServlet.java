package com.gym;

import java.io.IOException;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

import javax.servlet.RequestDispatcher;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

@WebServlet("/DashboardServlet")
public class DashboardServlet extends HttpServlet {
    private static final long serialVersionUID = 1L;

    protected void doGet(HttpServletRequest request, HttpServletResponse response) 
            throws ServletException, IOException {
        
        HttpSession session = request.getSession(false);
        
        if (session == null || session.getAttribute("userEmail") == null) {
            response.sendRedirect("login.html?error=Please login to access your dashboard");
            return;
        }

        String userEmail = (String) session.getAttribute("userEmail");
        String sql = "SELECT * FROM members WHERE email = ?";

        try (Connection conn = DBConnection.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            if (conn == null) {
                response.sendRedirect("login.html?error=Database Connection Error");
                return;
            }

            stmt.setString(1, userEmail);

            try (ResultSet rs = stmt.executeQuery()) {
                if (rs.next()) {
                    request.setAttribute("memberName", rs.getString("name"));
                    request.setAttribute("memberEmail", rs.getString("email"));
                    request.setAttribute("memberPhone", rs.getString("phone"));
                    request.setAttribute("memberPlan", rs.getString("membership"));
                    request.setAttribute("joinDate", rs.getDate("join_date"));
                    request.setAttribute("status", rs.getString("status"));

                    RequestDispatcher dispatcher = request.getRequestDispatcher("dashboard.jsp");
                    dispatcher.forward(request, response);
                } else {
                    session.invalidate();
                    response.sendRedirect("login.html?error=Member record not found");
                }
            }

        } catch (SQLException e) {
            e.printStackTrace();
            response.sendRedirect("login.html?error=Database error fetching dashboard");
        }
    }

    protected void doPost(HttpServletRequest request, HttpServletResponse response) 
            throws ServletException, IOException {
        doGet(request, response);
    }
}
