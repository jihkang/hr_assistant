"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getUser, isAuthenticated, logout, type UserInfo } from "@/lib/auth";

const DEPARTMENT_LABELS: Record<string, string> = {
  hr: "인사팀",
  dev: "개발팀",
  marketing: "마케팅팀",
  finance: "재무팀",
  sales: "영업팀",
  operations: "운영팀",
};

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<UserInfo | null>(null);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/");
      return;
    }
    setUser(getUser());
  }, [router]);

  const handleLogout = () => {
    logout();
    router.push("/");
  };

  if (!user) return null;

  const deptLabel = DEPARTMENT_LABELS[user.department] ?? user.department;

  return (
    <div style={styles.wrapper}>
      {/* Header */}
      <header style={styles.header}>
        <div style={styles.headerInner}>
          <h1 style={styles.logo}>HR Assistant</h1>
          <nav style={styles.nav}>
            <a href="#" style={styles.navLink}>대시보드</a>
            <a href="#" style={styles.navLink}>인사 관리</a>
            <a href="#" style={styles.navLink}>자산 관리</a>
            <a href="#" style={styles.navLink}>설정</a>
          </nav>
          <div style={styles.headerRight}>
            <span style={styles.userInfo}>
              {user.name} ({deptLabel})
            </span>
            <button onClick={handleLogout} style={styles.logoutBtn}>
              로그아웃
            </button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section style={styles.hero}>
        <h2 style={styles.heroTitle}>
          환영합니다, {user.name}님!
        </h2>
        <p style={styles.heroDesc}>
          {deptLabel} 소속 | HR Assistant에서 사내 인사 관리와 자산 관리를
          <br />
          효율적으로 처리하세요.
        </p>
      </section>

      {/* Stats */}
      <section style={styles.statsSection}>
        <div style={styles.statsGrid}>
          <div style={styles.statCard}>
            <div style={styles.statNumber}>0</div>
            <div style={styles.statLabel}>전체 직원 수</div>
          </div>
          <div style={styles.statCard}>
            <div style={styles.statNumber}>0</div>
            <div style={styles.statLabel}>부서 수</div>
          </div>
          <div style={styles.statCard}>
            <div style={styles.statNumber}>0</div>
            <div style={styles.statLabel}>관리 자산</div>
          </div>
          <div style={styles.statCard}>
            <div style={styles.statNumber}>0</div>
            <div style={styles.statLabel}>이번 달 신규 입사</div>
          </div>
        </div>
      </section>

      {/* Feature Cards */}
      <section style={styles.featureSection}>
        <h3 style={styles.sectionTitle}>주요 기능</h3>
        <div style={styles.featureGrid}>
          {/* 인사 관리 */}
          <div style={styles.featureCard}>
            <div style={{ ...styles.featureIconWrap, background: "#dbeafe" }}>
              <span style={{ fontSize: 32 }}>👥</span>
            </div>
            <h4 style={styles.featureTitle}>인사 관리</h4>
            <p style={styles.featureDesc}>
              직원 정보 등록, 조직도 관리, 인사 발령 및 이력 관리를 한 곳에서 처리하세요.
            </p>
            <ul style={styles.featureList}>
              <li>직원 프로필 관리</li>
              <li>조직도 및 부서 관리</li>
              <li>인사 발령 이력</li>
              <li>직원 검색 및 필터링</li>
            </ul>
          </div>

          {/* 근태 관리 */}
          <div style={styles.featureCard}>
            <div style={{ ...styles.featureIconWrap, background: "#d1fae5" }}>
              <span style={{ fontSize: 32 }}>📋</span>
            </div>
            <h4 style={styles.featureTitle}>근태 관리</h4>
            <p style={styles.featureDesc}>
              출퇴근 기록, 연차 관리, 초과 근무 등 근태 현황을 실시간으로 파악하세요.
            </p>
            <ul style={styles.featureList}>
              <li>출퇴근 기록 관리</li>
              <li>연차 / 휴가 신청 및 승인</li>
              <li>초과 근무 관리</li>
              <li>근태 현황 대시보드</li>
            </ul>
          </div>

          {/* 자산 관리 */}
          <div style={styles.featureCard}>
            <div style={{ ...styles.featureIconWrap, background: "#fef3c7" }}>
              <span style={{ fontSize: 32 }}>💰</span>
            </div>
            <h4 style={styles.featureTitle}>자산 관리</h4>
            <p style={styles.featureDesc}>
              회사 보유 자산의 등록, 배정, 반납, 폐기까지 전체 라이프사이클을 관리하세요.
            </p>
            <ul style={styles.featureList}>
              <li>IT 장비 (노트북, 모니터 등)</li>
              <li>사무용품 및 비품 관리</li>
              <li>자산 배정 및 반납 이력</li>
              <li>자산 현황 리포트</li>
            </ul>
          </div>

          {/* 리포트 */}
          <div style={styles.featureCard}>
            <div style={{ ...styles.featureIconWrap, background: "#ede9fe" }}>
              <span style={{ fontSize: 32 }}>📊</span>
            </div>
            <h4 style={styles.featureTitle}>데이터 분석 및 리포트</h4>
            <p style={styles.featureDesc}>
              인사 데이터를 기반으로 다양한 분석 리포트를 생성하고 인사이트를 확보하세요.
            </p>
            <ul style={styles.featureList}>
              <li>부서별 / 직급별 통계</li>
              <li>이직률 분석</li>
              <li>자산 활용률 리포트</li>
              <li>맞춤형 리포트 생성</li>
            </ul>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer style={styles.footer}>
        <p>&copy; 2026 HR Assistant. All rights reserved.</p>
      </footer>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  wrapper: {
    minHeight: "100vh",
    background: "#f9fafb",
  },
  header: {
    background: "#ffffff",
    borderBottom: "1px solid #e5e7eb",
    position: "sticky",
    top: 0,
    zIndex: 100,
  },
  headerInner: {
    maxWidth: 1200,
    margin: "0 auto",
    padding: "0 24px",
    height: 64,
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
  },
  logo: {
    fontSize: 22,
    fontWeight: 800,
    color: "#2563eb",
  },
  nav: {
    display: "flex",
    gap: 32,
  },
  navLink: {
    fontSize: 15,
    fontWeight: 500,
    color: "#374151",
    cursor: "pointer",
    transition: "color 0.2s",
  },
  headerRight: {
    display: "flex",
    alignItems: "center",
    gap: 16,
  },
  userInfo: {
    fontSize: 14,
    fontWeight: 600,
    color: "#374151",
  },
  logoutBtn: {
    padding: "8px 20px",
    borderRadius: 6,
    border: "1px solid #d1d5db",
    background: "#ffffff",
    fontSize: 14,
    color: "#374151",
    cursor: "pointer",
  },
  hero: {
    textAlign: "center",
    padding: "80px 24px 60px",
    background: "linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%)",
    color: "#ffffff",
  },
  heroTitle: {
    fontSize: 40,
    fontWeight: 800,
    lineHeight: 1.3,
    marginBottom: 20,
    letterSpacing: "-0.02em",
  },
  heroDesc: {
    fontSize: 17,
    lineHeight: 1.7,
    opacity: 0.9,
    maxWidth: 640,
    margin: "0 auto",
  },
  statsSection: {
    maxWidth: 1200,
    margin: "-40px auto 0",
    padding: "0 24px",
    position: "relative",
    zIndex: 10,
  },
  statsGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(4, 1fr)",
    gap: 20,
  },
  statCard: {
    background: "#ffffff",
    borderRadius: 12,
    padding: "28px 24px",
    textAlign: "center",
    boxShadow: "0 4px 24px rgba(0,0,0,0.08)",
  },
  statNumber: {
    fontSize: 36,
    fontWeight: 800,
    color: "#2563eb",
    marginBottom: 6,
  },
  statLabel: {
    fontSize: 14,
    color: "#6b7280",
    fontWeight: 500,
  },
  featureSection: {
    maxWidth: 1200,
    margin: "0 auto",
    padding: "60px 24px 80px",
  },
  sectionTitle: {
    fontSize: 28,
    fontWeight: 700,
    color: "#111827",
    textAlign: "center",
    marginBottom: 48,
  },
  featureGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(2, 1fr)",
    gap: 24,
  },
  featureCard: {
    background: "#ffffff",
    borderRadius: 16,
    padding: "32px",
    border: "1px solid #e5e7eb",
    transition: "box-shadow 0.2s",
  },
  featureIconWrap: {
    width: 60,
    height: 60,
    borderRadius: 14,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 20,
  },
  featureTitle: {
    fontSize: 20,
    fontWeight: 700,
    color: "#111827",
    marginBottom: 10,
  },
  featureDesc: {
    fontSize: 15,
    color: "#6b7280",
    lineHeight: 1.6,
    marginBottom: 16,
  },
  featureList: {
    listStyle: "none",
    display: "flex",
    flexDirection: "column",
    gap: 8,
    fontSize: 14,
    color: "#374151",
  },
  footer: {
    textAlign: "center",
    padding: "24px",
    borderTop: "1px solid #e5e7eb",
    fontSize: 14,
    color: "#9ca3af",
    background: "#ffffff",
  },
};
