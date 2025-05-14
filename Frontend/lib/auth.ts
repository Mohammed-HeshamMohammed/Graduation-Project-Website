import jwt from "jsonwebtoken"

export function verifyAuth(request: Request) {
  try {
    // Get the authorization header
    const authHeader = request.headers.get("authorization")

    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      return {
        success: false,
        message: "Authorization header missing or invalid",
        status: 401,
      }
    }

    // Extract the token
    const token = authHeader.split(" ")[1]

    if (!token) {
      return {
        success: false,
        message: "Token missing",
        status: 401,
      }
    }

    // Verify the token
    const decoded = jwt.verify(token, process.env.JWT_SECRET || "your-secret-key")

    return {
      success: true,
      data: decoded as { userId: number; email: string; companyId: number },
    }
  } catch (error) {
    if (error instanceof jwt.JsonWebTokenError) {
      return {
        success: false,
        message: "Invalid token",
        status: 401,
      }
    }

    return {
      success: false,
      message: "Authentication error",
      status: 500,
    }
  }
}

