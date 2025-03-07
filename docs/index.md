
The `toc: true` setting in `_config.yml` enables the Table of Contents feature. It will automatically appear on the right side if you use a Jekyll-compatible theme like `jekyll-theme-minimal`.

### **Step 3: Test Your GitHub Pages**
Once you have committed these changes:

1. Go to your repository’s GitHub Pages URL (e.g., `https://yourusername.github.io/SegMantX/`).
2. You should see the **Table of Contents** appear on the right, and a **sidebar** (if the theme supports it) will show on the left.

---

### **Alternative: Use Custom HTML for the Sidebar**

If you want more control over the sidebar, you can add **custom HTML** to your `index.md` file. For example, you can manually create a left-side sidebar like this:

```markdown
<div style="display: flex;">
  <!-- Left Sidebar -->
  <div style="width: 250px; padding: 10px; border-right: 2px solid #ddd;">
    <h3>Quick Links</h3>
    <ul>
      <li><a href="installation.md">Installation</a></li>
      <li><a href="usage.md">Usage</a></li>
      <li><a href="manual.md">Manual</a></li>
    </ul>
  </div>

  <!-- Main Content -->
  <div style="flex-grow: 1; padding: 10px;">
    # SegMantX: Bioinformatics Tool

    Welcome to SegMantX, a powerful bioinformatics tool for DNA sequence alignment.

    ## Installation

    For a quick installation, see our [installation guide](installation.md).

    ## Quick Start

    Here’s a simple example of how to use SegMantX:

    ```bash
    python3 SegMantX.py chain_self_alignments --input_file myfile.fasta --output_file result.txt
    ```
  </div>
</div>
