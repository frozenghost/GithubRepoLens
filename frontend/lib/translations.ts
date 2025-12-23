export type Translation = {
  hero: {
    title: string;
    subtitle: string;
    placeholder: string;
    analyze: string;
    scanning: string;
  };
  status: {
    idle: string;
    scanning: string;
    reading: string;
    analyzing: string;
    completed: string;
    error: string;
  };
  tools: {
    read_file: string;
    list_directory: string;
    get_repo_structure: string;
  };
  report: {
    title: string;
    download_pdf: string;
    generating_pdf: string;
  };
};

export const translations: Record<"en" | "zh", Translation> = {
  en: {
    hero: {
      title: "GitHub Repository Lens",
      subtitle: "Deep insights into your codebase through AI-powered analysis.",
      placeholder: "Paste GitHub repository URL here...",
      analyze: "Analyze Repository",
      scanning: "Scanning...",
    },
    status: {
      idle: "Ready to analyze",
      scanning: "Scanning repository structure...",
      reading: "Reading file contents...",
      analyzing: "Analyzing code patterns...",
      completed: "Analysis completed",
      error: "Analysis failed",
    },
    tools: {
      read_file: "Reading file",
      list_directory: "Listing directory",
      get_repo_structure: "Fetching structure",
    },
    report: {
      title: "Analysis Report",
      download_pdf: "Download PDF",
      generating_pdf: "Generating PDF...",
    },
  },
  zh: {
    hero: {
      title: "GitHub 仓库透视镜",
      subtitle: "通过 AI 深度分析，洞察代码库的每一个细节。",
      placeholder: "在此粘贴 GitHub 仓库链接...",
      analyze: "开始分析",
      scanning: "扫描中...",
    },
    status: {
      idle: "准备就绪",
      scanning: "正在扫描仓库结构...",
      reading: "正在读取文件内容...",
      analyzing: "正在分析代码模式...",
      completed: "分析完成",
      error: "分析失败",
    },
    tools: {
      read_file: "读取文件",
      list_directory: "列出目录",
      get_repo_structure: "获取结构",
    },
    report: {
      title: "分析报告",
      download_pdf: "下载 PDF",
      generating_pdf: "正在生成 PDF...",
    },
  },
};

export type Locale = keyof typeof translations;

