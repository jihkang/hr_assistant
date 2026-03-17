"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { signupSchema, type SignupFormData } from "@/lib/validations/signup";

type FieldErrors = Partial<Record<keyof SignupFormData, string>>;

export default function SignupPage() {
  const router = useRouter();
  const [form, setForm] = useState<SignupFormData>({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
    department: "",
  });
  const [errors, setErrors] = useState<FieldErrors>({});

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
    if (errors[name as keyof SignupFormData]) {
      setErrors({ ...errors, [name]: undefined });
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const result = signupSchema.safeParse(form);
    if (!result.success) {
      const fieldErrors: FieldErrors = {};
      for (const issue of result.error.issues) {
        const field = issue.path[0] as keyof SignupFormData;
        if (!fieldErrors[field]) {
          fieldErrors[field] = issue.message;
        }
      }
      setErrors(fieldErrors);
      return;
    }

    setErrors({});
    // TODO: 실제 API 연동
    router.push("/dashboard");
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
          <div style={styles.featureList}>
            <div style={styles.featureItem}>
              <span style={styles.featureIcon}>👥</span>
              <span>직원 정보 및 조직 관리</span>
            </div>
            <div style={styles.featureItem}>
              <span style={styles.featureIcon}>📋</span>
              <span>근태 및 휴가 관리</span>
            </div>
            <div style={styles.featureItem}>
              <span style={styles.featureIcon}>💰</span>
              <span>급여 및 자산 관리</span>
            </div>
            <div style={styles.featureItem}>
              <span style={styles.featureIcon}>📊</span>
              <span>인사 데이터 분석 및 리포트</span>
            </div>
          </div>
        </div>
      </div>

      <div style={styles.right}>
        <form onSubmit={handleSubmit} style={styles.form}>
          <h2 style={styles.formTitle}>회원가입</h2>
          <p style={styles.formSubtitle}>
            HR Assistant에 오신 것을 환영합니다
          </p>

          {Object.keys(errors).length > 0 && (
            <div style={styles.error}>
              입력 정보를 확인해주세요.
            </div>
          )}

          <div style={styles.field}>
            <label style={styles.label}>이름</label>
            <input
              type="text"
              name="name"
              value={form.name}
              onChange={handleChange}
              placeholder="홍길동"
              style={errors.name ? { ...styles.input, ...styles.inputError } : styles.input}
            />
            {errors.name && <p style={styles.fieldError}>{errors.name}</p>}
          </div>

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
            <label style={styles.label}>부서</label>
            <select
              name="department"
              value={form.department}
              onChange={handleChange}
              style={errors.department ? { ...styles.input, ...styles.inputError } : styles.input}
            >
              <option value="">부서를 선택하세요</option>
              <option value="hr">인사팀</option>
              <option value="dev">개발팀</option>
              <option value="marketing">마케팅팀</option>
              <option value="finance">재무팀</option>
              <option value="sales">영업팀</option>
              <option value="operations">운영팀</option>
            </select>
            {errors.department && <p style={styles.fieldError}>{errors.department}</p>}
          </div>

          <div style={styles.field}>
            <label style={styles.label}>비밀번호</label>
            <input
              type="password"
              name="password"
              value={form.password}
              onChange={handleChange}
              placeholder="영문, 숫자 포함 8자 이상"
              style={errors.password ? { ...styles.input, ...styles.inputError } : styles.input}
            />
            {errors.password && <p style={styles.fieldError}>{errors.password}</p>}
          </div>

          <div style={styles.field}>
            <label style={styles.label}>비밀번호 확인</label>
            <input
              type="password"
              name="confirmPassword"
              value={form.confirmPassword}
              onChange={handleChange}
              placeholder="비밀번호를 다시 입력하세요"
              style={errors.confirmPassword ? { ...styles.input, ...styles.inputError } : styles.input}
            />
            {errors.confirmPassword && <p style={styles.fieldError}>{errors.confirmPassword}</p>}
          </div>

          <button type="submit" style={styles.button}>
            가입하기
          </button>

          <p style={styles.loginLink}>
            이미 계정이 있으신가요?{" "}
            <a href="/login" style={styles.link}>
              로그인
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
    marginBottom: 48,
  },
  featureList: {
    display: "flex",
    flexDirection: "column",
    gap: 20,
  },
  featureItem: {
    display: "flex",
    alignItems: "center",
    gap: 16,
    fontSize: 17,
    opacity: 0.9,
  },
  featureIcon: {
    fontSize: 24,
    width: 40,
    height: 40,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: "rgba(255,255,255,0.15)",
    borderRadius: 10,
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
    transition: "border-color 0.2s",
    background: "#ffffff",
    color: "#111827",
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
    transition: "background 0.2s",
  },
  loginLink: {
    textAlign: "center",
    marginTop: 20,
    fontSize: 14,
    color: "#6b7280",
  },
  link: {
    color: "#2563eb",
    fontWeight: 600,
  },
  inputError: {
    borderColor: "#ef4444",
  },
  fieldError: {
    color: "#ef4444",
    fontSize: 13,
    marginTop: 4,
  },
};
