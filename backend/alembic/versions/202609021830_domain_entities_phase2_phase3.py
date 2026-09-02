"""domain entities phase2 phase3

Revision ID: 202609021830
Revises: 202609021750
Create Date: 2026-09-02 18:30:00
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "202609021830"
down_revision = "202609021750"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("organizations", sa.Column("created_by", sa.Uuid(), nullable=True))
    op.add_column("users", sa.Column("created_by", sa.Uuid(), nullable=True))
    op.add_column("memberships", sa.Column("created_by", sa.Uuid(), nullable=True))
    op.create_index(op.f("ix_organizations_created_by"), "organizations", ["created_by"], unique=False)
    op.create_index(op.f("ix_users_created_by"), "users", ["created_by"], unique=False)
    op.create_index(op.f("ix_memberships_created_by"), "memberships", ["created_by"], unique=False)

    op.create_table(
        "knowledge_categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("category_type", sa.String(length=64), nullable=False, server_default="custom"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_id"], ["knowledge_categories.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "slug", name="uq_category_org_slug"),
    )
    op.create_index(op.f("ix_knowledge_categories_organization_id"), "knowledge_categories", ["organization_id"], unique=False)
    op.create_index(op.f("ix_knowledge_categories_parent_id"), "knowledge_categories", ["parent_id"], unique=False)
    op.create_index(op.f("ix_knowledge_categories_status"), "knowledge_categories", ["status"], unique=False)
    op.create_index(op.f("ix_knowledge_categories_created_by"), "knowledge_categories", ["created_by"], unique=False)

    op.create_table(
        "knowledge_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("item_type", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["category_id"], ["knowledge_categories.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_knowledge_items_organization_id"), "knowledge_items", ["organization_id"], unique=False)
    op.create_index(op.f("ix_knowledge_items_category_id"), "knowledge_items", ["category_id"], unique=False)
    op.create_index(op.f("ix_knowledge_items_item_type"), "knowledge_items", ["item_type"], unique=False)
    op.create_index(op.f("ix_knowledge_items_status"), "knowledge_items", ["status"], unique=False)
    op.create_index(op.f("ix_knowledge_items_created_by"), "knowledge_items", ["created_by"], unique=False)

    op.create_table(
        "portfolio_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("knowledge_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_code", sa.String(length=64), nullable=False),
        sa.Column("project_name", sa.String(length=255), nullable=False),
        sa.Column("primary_url", sa.String(length=1024), nullable=True),
        sa.Column("capabilities", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("responsibilities", sa.Text(), nullable=True),
        sa.Column("technologies", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("implementation_details", sa.Text(), nullable=True),
        sa.Column("outcomes", sa.Text(), nullable=True),
        sa.Column("evidence_boundaries", sa.Text(), nullable=True),
        sa.Column("restrictions", sa.Text(), nullable=True),
        sa.Column("additional_urls", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("related_proposal_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["knowledge_item_id"], ["knowledge_items.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("knowledge_item_id"),
        sa.UniqueConstraint("organization_id", "project_code", name="uq_portfolio_project_code"),
    )
    op.create_index(op.f("ix_portfolio_items_organization_id"), "portfolio_items", ["organization_id"], unique=False)
    op.create_index(op.f("ix_portfolio_items_knowledge_item_id"), "portfolio_items", ["knowledge_item_id"], unique=False)
    op.create_index(op.f("ix_portfolio_items_project_code"), "portfolio_items", ["project_code"], unique=False)
    op.create_index(op.f("ix_portfolio_items_created_by"), "portfolio_items", ["created_by"], unique=False)

    op.create_table(
        "proposal_examples",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("knowledge_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_title", sa.String(length=255), nullable=False),
        sa.Column("job_description", sa.Text(), nullable=False),
        sa.Column("screening_questions", sa.Text(), nullable=True),
        sa.Column("submitted_proposal", sa.Text(), nullable=False),
        sa.Column("outcome", sa.String(length=32), nullable=False),
        sa.Column("client_name", sa.String(length=255), nullable=True),
        sa.Column("job_category", sa.String(length=128), nullable=True),
        sa.Column("job_type", sa.String(length=128), nullable=True),
        sa.Column("technologies", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("reusable_patterns", sa.Text(), nullable=True),
        sa.Column("restrictions", sa.Text(), nullable=True),
        sa.Column("related_portfolio_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["knowledge_item_id"], ["knowledge_items.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("knowledge_item_id"),
    )
    op.create_index(op.f("ix_proposal_examples_organization_id"), "proposal_examples", ["organization_id"], unique=False)
    op.create_index(op.f("ix_proposal_examples_knowledge_item_id"), "proposal_examples", ["knowledge_item_id"], unique=False)
    op.create_index(op.f("ix_proposal_examples_outcome"), "proposal_examples", ["outcome"], unique=False)
    op.create_index(op.f("ix_proposal_examples_created_by"), "proposal_examples", ["created_by"], unique=False)

    op.create_table(
        "proposal_example_qa",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("proposal_example_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["proposal_example_id"], ["proposal_examples.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_proposal_example_qa_organization_id"), "proposal_example_qa", ["organization_id"], unique=False)
    op.create_index(op.f("ix_proposal_example_qa_proposal_example_id"), "proposal_example_qa", ["proposal_example_id"], unique=False)
    op.create_index(op.f("ix_proposal_example_qa_created_by"), "proposal_example_qa", ["created_by"], unique=False)

    op.create_table(
        "app_sections",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("section_type", sa.String(length=64), nullable=False, server_default="authoritative"),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "slug", name="uq_app_section_org_slug"),
    )
    op.create_index(op.f("ix_app_sections_organization_id"), "app_sections", ["organization_id"], unique=False)
    op.create_index(op.f("ix_app_sections_status"), "app_sections", ["status"], unique=False)
    op.create_index(op.f("ix_app_sections_created_by"), "app_sections", ["created_by"], unique=False)

    op.create_table(
        "tags",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("tag_type", sa.String(length=64), nullable=False, server_default="skill"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "name", "tag_type", name="uq_tag_org_name_type"),
    )
    op.create_index(op.f("ix_tags_organization_id"), "tags", ["organization_id"], unique=False)
    op.create_index(op.f("ix_tags_created_by"), "tags", ["created_by"], unique=False)

    op.create_table(
        "tag_links",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tag_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_type", sa.String(length=64), nullable=False),
        sa.Column("entity_id", sa.Uuid(), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "tag_id", "entity_type", "entity_id", name="uq_tag_link"),
    )
    op.create_index(op.f("ix_tag_links_organization_id"), "tag_links", ["organization_id"], unique=False)
    op.create_index(op.f("ix_tag_links_tag_id"), "tag_links", ["tag_id"], unique=False)
    op.create_index(op.f("ix_tag_links_entity_type"), "tag_links", ["entity_type"], unique=False)
    op.create_index(op.f("ix_tag_links_entity_id"), "tag_links", ["entity_id"], unique=False)
    op.create_index(op.f("ix_tag_links_created_by"), "tag_links", ["created_by"], unique=False)

    op.create_table(
        "jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("latest_user_instruction", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_jobs_organization_id"), "jobs", ["organization_id"], unique=False)
    op.create_index(op.f("ix_jobs_status"), "jobs", ["status"], unique=False)
    op.create_index(op.f("ix_jobs_created_by"), "jobs", ["created_by"], unique=False)

    op.create_table(
        "job_screening_questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_job_screening_questions_organization_id"), "job_screening_questions", ["organization_id"], unique=False)
    op.create_index(op.f("ix_job_screening_questions_job_id"), "job_screening_questions", ["job_id"], unique=False)
    op.create_index(op.f("ix_job_screening_questions_created_by"), "job_screening_questions", ["created_by"], unique=False)

    op.create_table(
        "proposal_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("proposal_text", sa.Text(), nullable=False),
        sa.Column("screening_answers", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("selected_sources", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("analysis_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("provider", sa.String(length=64), nullable=False, server_default="local-template"),
        sa.Column("model", sa.String(length=128), nullable=False, server_default="deterministic-v1"),
        sa.Column("generation_status", sa.String(length=32), nullable=False, server_default="completed"),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_proposal_runs_organization_id"), "proposal_runs", ["organization_id"], unique=False)
    op.create_index(op.f("ix_proposal_runs_job_id"), "proposal_runs", ["job_id"], unique=False)
    op.create_index(op.f("ix_proposal_runs_created_by"), "proposal_runs", ["created_by"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_proposal_runs_created_by"), table_name="proposal_runs")
    op.drop_index(op.f("ix_proposal_runs_job_id"), table_name="proposal_runs")
    op.drop_index(op.f("ix_proposal_runs_organization_id"), table_name="proposal_runs")
    op.drop_table("proposal_runs")

    op.drop_index(op.f("ix_job_screening_questions_created_by"), table_name="job_screening_questions")
    op.drop_index(op.f("ix_job_screening_questions_job_id"), table_name="job_screening_questions")
    op.drop_index(op.f("ix_job_screening_questions_organization_id"), table_name="job_screening_questions")
    op.drop_table("job_screening_questions")

    op.drop_index(op.f("ix_jobs_created_by"), table_name="jobs")
    op.drop_index(op.f("ix_jobs_status"), table_name="jobs")
    op.drop_index(op.f("ix_jobs_organization_id"), table_name="jobs")
    op.drop_table("jobs")

    op.drop_index(op.f("ix_tag_links_created_by"), table_name="tag_links")
    op.drop_index(op.f("ix_tag_links_entity_id"), table_name="tag_links")
    op.drop_index(op.f("ix_tag_links_entity_type"), table_name="tag_links")
    op.drop_index(op.f("ix_tag_links_tag_id"), table_name="tag_links")
    op.drop_index(op.f("ix_tag_links_organization_id"), table_name="tag_links")
    op.drop_table("tag_links")

    op.drop_index(op.f("ix_tags_created_by"), table_name="tags")
    op.drop_index(op.f("ix_tags_organization_id"), table_name="tags")
    op.drop_table("tags")

    op.drop_index(op.f("ix_app_sections_created_by"), table_name="app_sections")
    op.drop_index(op.f("ix_app_sections_status"), table_name="app_sections")
    op.drop_index(op.f("ix_app_sections_organization_id"), table_name="app_sections")
    op.drop_table("app_sections")

    op.drop_index(op.f("ix_proposal_example_qa_created_by"), table_name="proposal_example_qa")
    op.drop_index(op.f("ix_proposal_example_qa_proposal_example_id"), table_name="proposal_example_qa")
    op.drop_index(op.f("ix_proposal_example_qa_organization_id"), table_name="proposal_example_qa")
    op.drop_table("proposal_example_qa")

    op.drop_index(op.f("ix_proposal_examples_created_by"), table_name="proposal_examples")
    op.drop_index(op.f("ix_proposal_examples_outcome"), table_name="proposal_examples")
    op.drop_index(op.f("ix_proposal_examples_knowledge_item_id"), table_name="proposal_examples")
    op.drop_index(op.f("ix_proposal_examples_organization_id"), table_name="proposal_examples")
    op.drop_table("proposal_examples")

    op.drop_index(op.f("ix_portfolio_items_created_by"), table_name="portfolio_items")
    op.drop_index(op.f("ix_portfolio_items_project_code"), table_name="portfolio_items")
    op.drop_index(op.f("ix_portfolio_items_knowledge_item_id"), table_name="portfolio_items")
    op.drop_index(op.f("ix_portfolio_items_organization_id"), table_name="portfolio_items")
    op.drop_table("portfolio_items")

    op.drop_index(op.f("ix_knowledge_items_created_by"), table_name="knowledge_items")
    op.drop_index(op.f("ix_knowledge_items_status"), table_name="knowledge_items")
    op.drop_index(op.f("ix_knowledge_items_item_type"), table_name="knowledge_items")
    op.drop_index(op.f("ix_knowledge_items_category_id"), table_name="knowledge_items")
    op.drop_index(op.f("ix_knowledge_items_organization_id"), table_name="knowledge_items")
    op.drop_table("knowledge_items")

    op.drop_index(op.f("ix_knowledge_categories_created_by"), table_name="knowledge_categories")
    op.drop_index(op.f("ix_knowledge_categories_status"), table_name="knowledge_categories")
    op.drop_index(op.f("ix_knowledge_categories_parent_id"), table_name="knowledge_categories")
    op.drop_index(op.f("ix_knowledge_categories_organization_id"), table_name="knowledge_categories")
    op.drop_table("knowledge_categories")

    op.drop_index(op.f("ix_memberships_created_by"), table_name="memberships")
    op.drop_index(op.f("ix_users_created_by"), table_name="users")
    op.drop_index(op.f("ix_organizations_created_by"), table_name="organizations")
    op.drop_column("memberships", "created_by")
    op.drop_column("users", "created_by")
    op.drop_column("organizations", "created_by")
