import styles from "./Header.module.css";

export default function Header() {
  return (
    <header className={styles.header}>
      <div className={styles.headerBrand}>
        <div className={styles.titleWrapper}>
          <h1 className={styles.headerTitle}>NeuralSketch</h1>
          <p className={styles.headerSubtitle}>Real-time AI Drawing Recognition</p>
        </div>
      </div>
    </header>
  );
}
