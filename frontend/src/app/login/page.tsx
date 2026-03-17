"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { loginSchema, type LoginFormData } from "@/lib/validations/login";
import { login } from "@/lib/auth";

type FieldErrors = Partial<Record<keyof LoginFormData, string>>;

export default function LoginPage() {
  const router = useRouter();
  const [form, setForm] = useState<LoginFormData>({
    email: "",
    password: "",
  });
  const [errors, setErrors] = useState<FieldErrors>({});
  const [serverError, setServerError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
    if (errors[name as keyof LoginFormData]) {
      setErrors({ ...errors, [name]: undefined });
    }
    if (serverError) setServerError("");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const result = loginSchema.safeParse(form);
    if (!result.success) {
      const fieldErrors: FieldErrors = {};
      for (const issue of result.error.issues) {
        const field = issue.path[0] as keyof LoginFormData;
        if (!fieldErrors[field]) {
          fieldErrors[field] = issue.message;
        }
      }
      setErrors(fieldErrors);
      return;
    }

    setErrors({});
    setLoading(true);

    try {
      await login(form.email, form.password);
      router.push("/dashboard");
    } catch (err) {
      setServerError(err instanceof Error ? err.message : "로그인에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.left}>
        <div style={styles.brandContent}>
          <h1 style={styles.brandTitle}>HR Assistant</h1>
          <p style={styles.brandSubtitle}>
            사내 인사 관리 및 자산 관리를 위한
            <br />
            통합 솔루션
          </p>
        </div>
      </div>

      <div style={styles.right}>
        <form onSubmit={handleSubmit} style={styles.form}>
          <h2 style={styles.formTitle}>로그인</h2>
          <p style={styles.formSubtitle}>계정에 로그인하세요</p>

          {serverError && <div style={styles.error}>{serverError}</div>}

          <div style={styles.field}>
            <label style={styles.label}>이메일</label>
            <input
              type="email"
              name="email"
              value={form.email}
              onChange={handleChange}
              placeholder="example@company.com"
              style={errors.email ? { ...styles.input, ...styles.inputError } : styles.input}
            />
            {errors.email && <p style={styles.fieldError}>{errors.email}</p>}
          </div>

          <div style={styles.field}>
            <label style={styles.label}>비밀번호</label>
            <input
              type="password"
              name="password"
              value={form.password}
              onChange={handleChange}
              placeholder="비밀번호를 입력하세요"
              style={errors.password ? { ...styles.input, ...styles.inputError } : styles.input}
            />
            {errors.password && <p style={styles.fieldError}>{errors.password}</p>}
          </div>

          <button type="submit" style={styles.button} disabled={loading}>
            {loading ? "로그인 중..." : "로그인"}
          </button>

          <p style={styles.signupLink}>
            계정이 없으신가요?{" "}
            <a href="/" style={styles.link}>
              회원가입
            </a>
          </p>
        </form>
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: "flex",
    minHeight: "100vh",
  },
  left: {
    flex: 1,
    background: "linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "40px",
    color: "#ffffff",
  },
  brandContent: {
    maxWidth: 480,
  },
  brandTitle: {
    fontSize: 48,
    fontWeight: 800,
    marginBottom: 16,
    letterSpacing: "-0.02em",
  },
  brandSubtitle: {
    fontSize: 20,
    lineHeight: 1.6,
    opacity: 0.9,
  },
  right: {
    flex: 1,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "40px",
    background: "#f9fafb",
  },
  form: {
    width: "100%",
    maxWidth: 420,
  },
  formTitle: {
    fontSize: 28,
    fontWeight: 700,
    color: "#111827",
    marginBottom: 8,
  },
  formSubtitle: {
    fontSize: 15,
    color: "#6b7280",
    marginBottom: 32,
  },
  error: {
    background: "#fef2f2",
    color: "#dc2626",
    padding: "12px 16px",
    borderRadius: 8,
    fontSize: 14,
    marginBottom: 20,
    border: "1px solid #fecaca",
  },
  field: {
    marginBottom: 20,
  },
  label: {
    display: "block",
    fontSize: 14,
    fontWeight: 600,
    color: "#374151",
    marginBottom: 6,
  },
  input: {
    width: "100%",
    padding: "12px 14px",
    borderRadius: 8,
    border: "1px solid #d1d5db",
    fontSize: 15,
    outline: "none",
    background: "#ffffff",
    color: "#111827",
  },
  inputError: {
    borderColor: "#ef4444",
  },
  fieldError: {
    color: "#ef4444",
    fontSize: 13,
    marginTop: 4,
  },
  button: {
    width: "100%",
    padding: "14px",
    borderRadius: 8,
    border: "none",
    background: "#2563eb",
    color: "#ffffff",
    fontSize: 16,
    fontWeight: 600,
    cursor: "pointer",
    marginTop: 8,
  },
  signupLink: {
    textAlign: "center",
    marginTop: 20,
    fontSize: 14,
    color: "#6b7280",
  },
  link: {
    color: "#2563eb",
    fontWeight: 600,
  },
};
