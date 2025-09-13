import React, { useState, useEffect } from 'react';
import {
  Modal,
  Form,
  Input,
  Select,
  DatePicker,
  InputNumber,
  Button,
  Space,
  Tag,
  message,
  Divider
} from 'antd';
import { PlusOutlined, MinusCircleOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';

const { TextArea } = Input;
const { Option } = Select;

interface Paper {
  id?: number;
  title: string;
  authors: string | string[];
  abstract?: string;
  publication_date?: string;
  venue?: string;
  paper_type?: string;
  arxiv_id?: string;
  doi?: string;
  pdf_url?: string;
  website_url?: string;
  citation_count?: number;
  research_areas?: string | string[];
  keywords?: string | string[];
  lab_id: number;
}

interface PaperFormModalProps {
  visible: boolean;
  onCancel: () => void;
  onSuccess: () => void;
  paper?: Paper | null;
  mode: 'create' | 'edit';
  labId: number;
}

const PaperFormModal: React.FC<PaperFormModalProps> = ({
  visible,
  onCancel,
  onSuccess,
  paper,
  mode,
  labId
}) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [authors, setAuthors] = useState<string[]>(['']);
  const [researchAreas, setResearchAreas] = useState<string[]>([]);
  const [keywords, setKeywords] = useState<string[]>([]);

  useEffect(() => {
    if (visible) {
      if (mode === 'edit' && paper) {
        // Parse authors
        let authorsList: string[] = [];
        if (typeof paper.authors === 'string') {
          try {
            authorsList = JSON.parse(paper.authors);
          } catch {
            authorsList = paper.authors.split(',').map(a => a.trim());
          }
        } else if (Array.isArray(paper.authors)) {
          authorsList = paper.authors;
        }

        // Parse research areas
        let areasList: string[] = [];
        if (typeof paper.research_areas === 'string') {
          try {
            areasList = JSON.parse(paper.research_areas);
          } catch {
            areasList = paper.research_areas.split(',').map(a => a.trim());
          }
        } else if (Array.isArray(paper.research_areas)) {
          areasList = paper.research_areas;
        }

        // Parse keywords
        let keywordsList: string[] = [];
        if (typeof paper.keywords === 'string') {
          try {
            keywordsList = JSON.parse(paper.keywords);
          } catch {
            keywordsList = paper.keywords.split(',').map(k => k.trim());
          }
        } else if (Array.isArray(paper.keywords)) {
          keywordsList = paper.keywords;
        }

        setAuthors(authorsList.length > 0 ? authorsList : ['']);
        setResearchAreas(areasList);
        setKeywords(keywordsList);

        form.setFieldsValue({
          title: paper.title,
          abstract: paper.abstract,
          publication_date: paper.publication_date ? dayjs(paper.publication_date) : null,
          venue: paper.venue,
          paper_type: paper.paper_type || 'journal',
          arxiv_id: paper.arxiv_id,
          doi: paper.doi,
          pdf_url: paper.pdf_url,
          website_url: paper.website_url,
          citation_count: paper.citation_count || 0
        });
      } else {
        // Reset for create mode
        setAuthors(['']);
        setResearchAreas([]);
        setKeywords([]);
        form.resetFields();
        form.setFieldsValue({
          paper_type: 'journal',
          citation_count: 0
        });
      }
    }
  }, [visible, mode, paper, form]);

  const handleSubmit = async (values: any) => {
    try {
      setLoading(true);

      const paperData = {
        ...values,
        authors: authors.filter(author => author.trim() !== ''),
        research_areas: researchAreas,
        keywords: keywords,
        publication_date: values.publication_date ? values.publication_date.format('YYYY-MM-DD') : null,
        lab_id: labId
      };

      const url = mode === 'edit' && paper 
        ? `http://127.0.0.1:8080/api/papers/${paper.id}`
        : 'http://127.0.0.1:8080/api/papers/';

      const method = mode === 'edit' ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(paperData)
      });

      if (response.ok) {
        const result = await response.json();
        message.success(mode === 'edit' ? 'Paper updated successfully!' : 'Paper created successfully!');
        onSuccess();
        onCancel();
      } else {
        const error = await response.json();
        message.error(`Failed to ${mode} paper: ${error.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error(`Error ${mode}ing paper:`, error);
      message.error(`Error ${mode}ing paper`);
    } finally {
      setLoading(false);
    }
  };

  const addAuthor = () => {
    setAuthors([...authors, '']);
  };

  const removeAuthor = (index: number) => {
    const newAuthors = authors.filter((_, i) => i !== index);
    setAuthors(newAuthors.length > 0 ? newAuthors : ['']);
  };

  const updateAuthor = (index: number, value: string) => {
    const newAuthors = [...authors];
    newAuthors[index] = value;
    setAuthors(newAuthors);
  };

  const addResearchArea = (value: string) => {
    if (value && !researchAreas.includes(value)) {
      setResearchAreas([...researchAreas, value]);
    }
  };

  const removeResearchArea = (area: string) => {
    setResearchAreas(researchAreas.filter(a => a !== area));
  };

  const addKeyword = (value: string) => {
    if (value && !keywords.includes(value)) {
      setKeywords([...keywords, value]);
    }
  };

  const removeKeyword = (keyword: string) => {
    setKeywords(keywords.filter(k => k !== keyword));
  };

  return (
    <Modal
      title={mode === 'edit' ? 'Edit Paper' : 'Add New Paper'}
      open={visible}
      onCancel={onCancel}
      footer={null}
      width={800}
      destroyOnClose
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
      >
        <Form.Item
          name="title"
          label="Title"
          rules={[{ required: true, message: 'Please enter paper title' }]}
        >
          <Input placeholder="Enter paper title" />
        </Form.Item>

        <Form.Item label="Authors" required>
          <Space direction="vertical" style={{ width: '100%' }}>
            {authors.map((author, index) => (
              <Space key={index} style={{ width: '100%' }}>
                <Input
                  placeholder={`Author ${index + 1}`}
                  value={author}
                  onChange={(e) => updateAuthor(index, e.target.value)}
                  style={{ flex: 1 }}
                />
                {authors.length > 1 && (
                  <Button
                    type="text"
                    icon={<MinusCircleOutlined />}
                    onClick={() => removeAuthor(index)}
                    danger
                  />
                )}
              </Space>
            ))}
            <Button
              type="dashed"
              onClick={addAuthor}
              icon={<PlusOutlined />}
              style={{ width: '100%' }}
            >
              Add Author
            </Button>
          </Space>
        </Form.Item>

        <Form.Item
          name="abstract"
          label="Abstract"
        >
          <TextArea
            rows={4}
            placeholder="Enter paper abstract"
          />
        </Form.Item>

        <Form.Item
          name="publication_date"
          label="Publication Date"
        >
          <DatePicker style={{ width: '100%' }} />
        </Form.Item>

        <Form.Item
          name="venue"
          label="Venue"
        >
          <Input placeholder="e.g., ICRA, NeurIPS, Nature Robotics" />
        </Form.Item>

        <Form.Item
          name="paper_type"
          label="Paper Type"
        >
          <Select>
            <Option value="journal">Journal</Option>
            <Option value="conference">Conference</Option>
            <Option value="preprint">Preprint</Option>
            <Option value="workshop">Workshop</Option>
            <Option value="book">Book Chapter</Option>
          </Select>
        </Form.Item>

        <Divider />

        <Form.Item
          name="arxiv_id"
          label="ArXiv ID"
        >
          <Input placeholder="e.g., 2301.12345" />
        </Form.Item>

        <Form.Item
          name="doi"
          label="DOI"
        >
          <Input placeholder="e.g., 10.1109/ICRA.2023.12345" />
        </Form.Item>

        <Form.Item
          name="pdf_url"
          label="PDF URL"
        >
          <Input placeholder="Direct link to PDF" />
        </Form.Item>

        <Form.Item
          name="website_url"
          label="Website URL"
        >
          <Input placeholder="Project website or paper page" />
        </Form.Item>

        <Form.Item
          name="citation_count"
          label="Citation Count"
        >
          <InputNumber min={0} style={{ width: '100%' }} />
        </Form.Item>

        <Divider />

        <Form.Item label="Research Areas">
          <Select
            placeholder="Add research areas"
            onSelect={(value: string | undefined) => value && addResearchArea(value)}
            value={undefined}
            style={{ width: '100%' }}
          >
            <Option value="manipulation">Manipulation</Option>
            <Option value="locomotion">Locomotion</Option>
            <Option value="learning">Learning</Option>
            <Option value="perception">Perception</Option>
            <Option value="navigation">Navigation</Option>
            <Option value="control">Control</Option>
            <Option value="human_robot_interaction">Human-Robot Interaction</Option>
            <Option value="simulation">Simulation</Option>
            <Option value="swarm_robotics">Swarm Robotics</Option>
            <Option value="soft_robotics">Soft Robotics</Option>
          </Select>
          <div style={{ marginTop: 8 }}>
            {researchAreas.map(area => (
              <Tag
                key={area}
                closable
                onClose={() => removeResearchArea(area)}
                style={{ marginBottom: 4 }}
              >
                {area}
              </Tag>
            ))}
          </div>
        </Form.Item>

        <Form.Item label="Keywords">
          <Input
            placeholder="Press Enter to add keyword"
            onPressEnter={(e) => {
              const value = (e.target as HTMLInputElement).value.trim();
              if (value) {
                addKeyword(value);
                (e.target as HTMLInputElement).value = '';
              }
            }}
          />
          <div style={{ marginTop: 8 }}>
            {keywords.map(keyword => (
              <Tag
                key={keyword}
                closable
                onClose={() => removeKeyword(keyword)}
                style={{ marginBottom: 4 }}
              >
                {keyword}
              </Tag>
            ))}
          </div>
        </Form.Item>

        <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
          <Space>
            <Button onClick={onCancel}>
              Cancel
            </Button>
            <Button type="primary" htmlType="submit" loading={loading}>
              {mode === 'edit' ? 'Update Paper' : 'Create Paper'}
            </Button>
          </Space>
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default PaperFormModal;