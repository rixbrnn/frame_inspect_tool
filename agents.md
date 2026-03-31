# agents.md - Frame Inspect Tool

## Project Relationship

This project (`frame_inspect_tool`) is the **implementation component** of a larger research effort. Changes here should be reflected in the academic documentation and vice versa.

### Related Project: TCC (Thesis)
- **Location**: `../tcc/`
- **Type**: LaTeX thesis/academic paper
- **Documentation**: `../tcc/claude/` - Contains planning docs, design decisions, and methodology
- **Main Document**: `../tcc/main.tex`

### Bidirectional Dependency

#### When changes occur in `frame_inspect_tool`:
1. **Code structure changes** → Update workflow documentation in `../tcc/claude/2026-03-19_complete-workflow.md`
2. **New features/modules** → Document in thesis methodology (capitulos)
3. **Performance improvements** → Update performance metrics in thesis
4. **API changes** → Update code examples in documentation
5. **New scripts added** → Update usage instructions in `../tcc/claude/` guides

#### When changes occur in `../tcc`:
1. **Methodology changes** → Implement corresponding validation in `src/validation/`
2. **Workflow updates** → Adjust `scripts/pipeline.py` and related tools
3. **New requirements** → Add features/analysis to codebase
4. **Protocol changes** → Update `scripts/` to match new procedures
5. **Dataset structure changes** → Modify recording organization in `recordings/`

### Key Integration Points

1. **Dataset Structure**:
   - Defined by: `recordings/` organization in this project
   - Documented in: `../tcc/COLETA_DADOS_PROTOCOLO.md`
   - Public dataset: https://huggingface.co/datasets/rixbrnn/frame_inspect_tool_data

2. **Workflow Documentation**:
   - Implementation: `scripts/` directory here
   - Methodology: `../tcc/claude/2026-03-19_complete-workflow.md`
   - Academic description: `../tcc/capitulos/` LaTeX files

3. **Technical Decisions**:
   - Code: `src/` modules
   - Rationale: `../tcc/claude/` planning documents
   - Examples: CFR conversion, shader warmup, codec selection

4. **Validation & Benchmarking**:
   - Tools: `scripts/validate_benchmark.py`, `src/validation/`
   - Protocol: `../tcc/COLETA_DADOS_PROTOCOLO.md`
   - Results: Referenced in thesis chapters

### Agent Instructions

When working on this project:
- ✅ **Always check** if changes need documentation updates in `../tcc/claude/`
- ✅ **Maintain consistency** between code behavior and thesis methodology
- ✅ **Cross-reference** technical decisions with planning documents
- ✅ **Update both projects** when making significant architectural changes
- ✅ **Keep README.md in sync** with thesis quick-start guides

### File Mapping

| Frame Inspect Tool | TCC Documentation |
|-------------------|-------------------|
| `README.md` | Quick reference in thesis intro |
| `DATASET.md` | `COLETA_DADOS_PROTOCOLO.md` |
| `scripts/validate_benchmark.py` | `claude/2026-03-19_complete-workflow.md` |
| `src/preprocessing/` | `claude/2026-03-19_cfr-conversion-implementation.md` |
| `recordings/` structure | `claude/2026-03-19_multi-game-recording-structure.md` |
| Performance metrics | Thesis results chapters |

### Session Documentation Protocol

**IMPORTANT**: When creating planning or documentation `.md` files during work sessions:

1. **Location**: All planning/session documents MUST go to `../tcc/claude/` directory
2. **Naming Convention**: `YYYY-MM-DD_topic-description.md`
   - Example: `2026-03-19_complete-workflow.md`
   - Example: `2026-03-22_new-feature-implementation.md`

3. **Required Metadata Header**:
```yaml
---
date: YYYY-MM-DD
user_input: "Original user question/request (exact quote)"
context: Brief description of what was discussed/implemented
---
```

4. **Content Structure**:
   - Clear explanation of what was requested
   - What was implemented or decided
   - Technical details and rationale
   - Code examples or references
   - Next steps or follow-up items

5. **When to Create Documentation**:
   - ✅ User requests a new feature or significant change
   - ✅ Design decisions that affect architecture
   - ✅ Workflow or protocol changes
   - ✅ Problem-solving sessions with important outcomes
   - ✅ Major refactoring or reorganization
   - ❌ Simple bug fixes or typo corrections
   - ❌ Routine maintenance tasks

6. **Cross-Reference**: Update `../tcc/claude/README.md` index when adding new documents

### Version Control Note

While these are separate Git repositories, they are **conceptually a single project**. Treat them as tightly coupled components that must stay synchronized.
