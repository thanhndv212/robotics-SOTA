import React, { useState, useEffect } from 'react';
import {
  Card,
  Typography,
  Space,
  Tag,
  Button,
  Modal,
  Form,
  Input,
  message,
  Avatar,
  Badge,
  Divider,
  List,
  Tooltip
} from 'antd';
import {
  TeamOutlined,
  UserOutlined,
  PlusOutlined,
  EditOutlined,
  ExperimentOutlined,
  LinkOutlined,
  FileTextOutlined
} from '@ant-design/icons';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

interface ResearchGroup {
  id: number;
  name: string;
  pi: string;
  focus_areas: string[];
  description?: string;
  website?: string;
  papers?: any[];
  paper_count?: number;
  lab_type: string;
}

interface Lab {
  id: number;
  name: string;
  pi: string;
  institution: string;
  city?: string;
  country?: string;
  latitude?: number;
  longitude?: number;
  focus_areas?: string[];
  website?: string;
  description?: string;
  established_year?: number;
  funding_sources?: string[];
  papers?: any[];
  paper_count?: number;
  lab_type?: string;
  parent_lab_id?: number;
  parent_lab?: string;
  sub_groups?: Lab[];
  sub_groups_count?: number;
}

interface ResearchGroupManagerProps {
  lab: Lab;
  onGroupCreated?: () => void;
}

const ResearchGroupManager: React.FC<ResearchGroupManagerProps> = ({
  lab,
  onGroupCreated
}) => {
  const [groups, setGroups] = useState<ResearchGroup[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    if (lab.lab_type === 'department') {
      loadResearchGroups();
    }
  }, [lab.id]);

  const loadResearchGroups = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8080/api/labs/${lab.id}/groups`
      );
      if (response.ok) {
        const data = await response.json();
        setGroups(data.research_groups || []);
      }
    } catch (error) {
      message.error('Failed to load research groups');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateGroup = async (values: any) => {
    try {
      const response = await fetch(
        `http://localhost:8080/api/labs/${lab.id}/groups`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            ...values,
            focus_areas: values.focus_areas?.split(',')
              .map((area: string) => area.trim()) || []
          }),
        }
      );

      if (response.ok) {
        message.success('Research group created successfully!');
        setModalVisible(false);
        form.resetFields();
        loadResearchGroups();
        onGroupCreated?.();
      } else {
        const error = await response.json();
        message.error(error.error || 'Failed to create research group');
      }
    } catch (error) {
      message.error('Network error occurred');
    }
  };

  const renderGroupCard = (group: ResearchGroup) => (
    <Card
      key={group.id}
      size="small"
      style={{ marginBottom: 12 }}
      actions={[
        <Button 
          type="text" 
          icon={<EditOutlined />} 
          size="small"
          key="edit"
        >
          Edit
        </Button>,
        group.website && (
          <Button
            type="text"
            icon={<LinkOutlined />}
            size="small"
            href={group.website}
            target="_blank"
            key="visit"
          >
            Visit
          </Button>
        )
      ].filter(Boolean)}
    >
      <Card.Meta
        avatar={
          <Avatar 
            icon={<UserOutlined />} 
            style={{ backgroundColor: '#1890ff' }}
          >
            {group.name.charAt(0)}
          </Avatar>
        }
        title={
          <Space>
            <Text strong>{group.name}</Text>
            {group.paper_count && (
              <Badge 
                count={group.paper_count} 
                style={{ backgroundColor: '#52c41a' }} 
              />
            )}
          </Space>
        }
        description={
          <Space direction="vertical" size="small" style={{ width: '100%' }}>
            <Text>
              <UserOutlined /> PI: {group.pi}
            </Text>
            {group.description && (
              <Paragraph
                ellipsis={{ rows: 2, expandable: true, symbol: 'more' }}
                style={{ marginBottom: 8 }}
              >
                {group.description}
              </Paragraph>
            )}
            <div>
              {group.focus_areas?.slice(0, 3).map((area) => (
                <Tag key={area} color="blue" style={{ marginBottom: 4 }}>
                  {area}
                </Tag>
              ))}
              {group.focus_areas && group.focus_areas.length > 3 && (
                <Tag color="default">+{group.focus_areas.length - 3} more</Tag>
              )}
            </div>
            {group.papers && group.papers.length > 0 && (
              <div>
                <Divider style={{ margin: '8px 0' }}>Recent Papers</Divider>
                <List
                  size="small"
                  dataSource={group.papers.slice(0, 3)}
                  renderItem={(paper: any) => (
                    <List.Item
                      actions={[
                        paper.pdf_url && (
                          <Tooltip title="View PDF">
                            <Button
                              type="link"
                              icon={<FileTextOutlined />}
                              size="small"
                              href={paper.pdf_url}
                              target="_blank"
                            />
                          </Tooltip>
                        )
                      ].filter(Boolean)}
                    >
                      <List.Item.Meta
                        title={
                          <Text 
                            style={{ fontSize: '12px' }}
                            ellipsis={{ tooltip: paper.title }}
                          >
                            {paper.title}
                          </Text>
                        }
                        description={
                          <Text type="secondary" style={{ fontSize: '11px' }}>
                            {paper.venue && `${paper.venue} • `}
                            {paper.publication_date && 
                              new Date(paper.publication_date).getFullYear()
                            }
                          </Text>
                        }
                      />
                    </List.Item>
                  )}
                />
                {group.papers.length > 3 && (
                  <Text type="secondary" style={{ fontSize: '11px' }}>
                    +{group.papers.length - 3} more papers
                  </Text>
                )}
              </div>
            )}
          </Space>
        }
      />
    </Card>
  );

  if (lab.lab_type !== 'department') {
    return null;
  }

  return (
    <Card
      title={
        <Space>
          <TeamOutlined />
          <span>Research Groups</span>
          <Badge count={groups.length} style={{ backgroundColor: '#1890ff' }} />
        </Space>
      }
      extra={
        <Button
          type="primary"
          icon={<PlusOutlined />}
          size="small"
          onClick={() => setModalVisible(true)}
        >
          Add Group
        </Button>
      }
      loading={loading}
      style={{ marginTop: 16 }}
    >
      {groups.length === 0 ? (
        <Text type="secondary">No research groups found</Text>
      ) : (
        <div>
          {groups.map(renderGroupCard)}
        </div>
      )}

      <Modal
        title="Create Research Group"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreateGroup}
        >
          <Form.Item
            name="name"
            label="Group Name"
            rules={[{ required: true, message: 'Please enter group name' }]}
          >
            <Input placeholder="e.g., Robot Learning Lab" />
          </Form.Item>

          <Form.Item
            name="pi"
            label="Principal Investigator"
            rules={[{ required: true, message: 'Please enter PI name' }]}
          >
            <Input placeholder="e.g., John Doe" />
          </Form.Item>

          <Form.Item
            name="website"
            label="Website"
          >
            <Input placeholder="https://..." />
          </Form.Item>

          <Form.Item
            name="focus_areas"
            label="Research Focus Areas"
            help="Separate multiple areas with commas"
          >
            <Input placeholder="e.g., Robot Learning, Deep RL, Manipulation" />
          </Form.Item>

          <Form.Item
            name="description"
            label="Description"
          >
            <TextArea
              rows={3}
              placeholder="Brief description of the research group..."
            />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                Create Group
              </Button>
              <Button onClick={() => setModalVisible(false)}>
                Cancel
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
};

export default ResearchGroupManager;