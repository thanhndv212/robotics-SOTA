import React, { useState, useEffect } from 'react';
import {
  Modal,
  Form,
  Input,
  InputNumber,
  Button,
  message,
  Row,
  Col,
  Tag,
  Space,
  Divider
} from 'antd';
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons';

const { TextArea } = Input;

interface Lab {
  id?: number;
  name: string;
  pi: string;
  institution: string;
  city: string;
  country: string;
  focus_areas?: string[];
  website?: string;
  latitude?: number;
  longitude?: number;
  established_year?: number;
  funding_sources?: string[];
  description?: string;
}

interface LabFormModalProps {
  visible: boolean;
  onCancel: () => void;
  onSuccess: () => void;
  lab?: Lab | null;
  mode: 'create' | 'edit';
}

const LabFormModal: React.FC<LabFormModalProps> = ({
  visible,
  onCancel,
  onSuccess,
  lab,
  mode
}) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [focusAreas, setFocusAreas] = useState<string[]>([]);
  const [fundingSources, setFundingSources] = useState<string[]>([]);
  const [newFocusArea, setNewFocusArea] = useState('');
  const [newFundingSource, setNewFundingSource] = useState('');

  useEffect(() => {
    if (visible && lab && mode === 'edit') {
      form.setFieldsValue({
        ...lab,
        focus_areas: lab.focus_areas || [],
        funding_sources: lab.funding_sources || []
      });
      setFocusAreas(lab.focus_areas || []);
      setFundingSources(lab.funding_sources || []);
    } else if (visible && mode === 'create') {
      form.resetFields();
      setFocusAreas([]);
      setFundingSources([]);
      setNewFocusArea('');
      setNewFundingSource('');
    }
  }, [visible, lab, mode, form]);

  const handleSubmit = async (values: any) => {
    setLoading(true);
    try {
      const labData = {
        ...values,
        focus_areas: focusAreas,
        funding_sources: fundingSources
      };

      const url = mode === 'create' 
        ? 'http://127.0.0.1:8080/api/labs/'
        : `http://127.0.0.1:8080/api/labs/${lab?.id}`;
      
      const method = mode === 'create' ? 'POST' : 'PUT';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(labData),
      });

      if (response.ok) {
        message.success(`Lab ${mode === 'create' ? 'created' : 'updated'} successfully!`);
        onSuccess();
        onCancel();
      } else {
        const error = await response.json();
        message.error(error.error || 'Operation failed');
      }
    } catch (error) {
      message.error('Network error occurred');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const addFocusArea = () => {
    if (newFocusArea.trim() && !focusAreas.includes(newFocusArea.trim())) {
      setFocusAreas([...focusAreas, newFocusArea.trim()]);
      setNewFocusArea('');
    }
  };

  const removeFocusArea = (area: string) => {
    setFocusAreas(focusAreas.filter(a => a !== area));
  };

  const addFundingSource = () => {
    if (newFundingSource.trim() && !fundingSources.includes(newFundingSource.trim())) {
      setFundingSources([...fundingSources, newFundingSource.trim()]);
      setNewFundingSource('');
    }
  };

  const removeFundingSource = (source: string) => {
    setFundingSources(fundingSources.filter(s => s !== source));
  };

  return (
    <Modal
      title={mode === 'create' ? '🚀 Create New Lab' : '✏️ Edit Lab'}
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
        initialValues={{
          latitude: 0,
          longitude: 0
        }}
      >
        <Divider orientation="left">Basic Information</Divider>
        
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="name"
              label="Lab Name"
              rules={[
                { required: true, message: 'Please enter lab name' },
                { min: 3, message: 'Lab name must be at least 3 characters' }
              ]}
            >
              <Input placeholder="Enter lab name" maxLength={200} />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="pi"
              label="Principal Investigator"
              rules={[
                { required: true, message: 'Please enter PI name' },
                { min: 2, message: 'PI name must be at least 2 characters' }
              ]}
            >
              <Input placeholder="Enter PI name" maxLength={100} />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="institution"
              label="Institution"
              rules={[{ required: true, message: 'Please enter institution' }]}
            >
              <Input placeholder="Enter institution" maxLength={200} />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="website"
              label="Website"
              rules={[
                { type: 'url', message: 'Please enter a valid URL' }
              ]}
            >
              <Input placeholder="https://example.com" maxLength={500} />
            </Form.Item>
          </Col>
        </Row>

        <Divider orientation="left">Location</Divider>
        
        <Row gutter={16}>
          <Col span={8}>
            <Form.Item
              name="city"
              label="City"
              rules={[{ required: true, message: 'Please enter city' }]}
            >
              <Input placeholder="Enter city" maxLength={100} />
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item
              name="country"
              label="Country"
              rules={[{ required: true, message: 'Please enter country' }]}
            >
              <Input placeholder="Enter country" maxLength={100} />
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item
              name="established_year"
              label="Established Year"
            >
              <InputNumber
                placeholder="Year"
                min={1900}
                max={new Date().getFullYear()}
                style={{ width: '100%' }}
              />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="latitude"
              label="Latitude"
              rules={[
                { type: 'number', min: -90, max: 90, message: 'Latitude must be between -90 and 90' }
              ]}
            >
              <InputNumber
                placeholder="Latitude"
                min={-90}
                max={90}
                step={0.000001}
                style={{ width: '100%' }}
              />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="longitude"
              label="Longitude"
              rules={[
                { type: 'number', min: -180, max: 180, message: 'Longitude must be between -180 and 180' }
              ]}
            >
              <InputNumber
                placeholder="Longitude"
                min={-180}
                max={180}
                step={0.000001}
                style={{ width: '100%' }}
              />
            </Form.Item>
          </Col>
        </Row>

        <Divider orientation="left">Research Information</Divider>

        <Form.Item label="Research Focus Areas">
          <Space direction="vertical" style={{ width: '100%' }}>
            <Input.Group compact>
              <Input
                style={{ width: 'calc(100% - 40px)' }}
                value={newFocusArea}
                onChange={(e) => setNewFocusArea(e.target.value)}
                placeholder="Add research focus area"
                onPressEnter={addFocusArea}
                maxLength={100}
              />
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={addFocusArea}
                disabled={!newFocusArea.trim()}
              />
            </Input.Group>
            <div>
              {focusAreas.map((area) => (
                <Tag
                  key={area}
                  closable
                  onClose={() => removeFocusArea(area)}
                  style={{ marginBottom: 8 }}
                  color="geekblue"
                >
                  {area}
                </Tag>
              ))}
            </div>
          </Space>
        </Form.Item>

        <Form.Item label="Funding Sources">
          <Space direction="vertical" style={{ width: '100%' }}>
            <Input.Group compact>
              <Input
                style={{ width: 'calc(100% - 40px)' }}
                value={newFundingSource}
                onChange={(e) => setNewFundingSource(e.target.value)}
                placeholder="Add funding source"
                onPressEnter={addFundingSource}
                maxLength={100}
              />
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={addFundingSource}
                disabled={!newFundingSource.trim()}
              />
            </Input.Group>
            <div>
              {fundingSources.map((source) => (
                <Tag
                  key={source}
                  closable
                  onClose={() => removeFundingSource(source)}
                  style={{ marginBottom: 8 }}
                  color="orange"
                >
                  {source}
                </Tag>
              ))}
            </div>
          </Space>
        </Form.Item>

        <Form.Item
          name="description"
          label="Description"
        >
          <TextArea
            rows={4}
            placeholder="Enter lab description, research goals, notable achievements, etc."
            maxLength={1000}
            showCount
          />
        </Form.Item>

        <Form.Item>
          <Space>
            <Button type="primary" htmlType="submit" loading={loading} size="large">
              {mode === 'create' ? '🚀 Create Lab' : '💾 Update Lab'}
            </Button>
            <Button onClick={onCancel} size="large">
              Cancel
            </Button>
          </Space>
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default LabFormModal;