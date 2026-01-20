import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { toast } from 'react-toastify';
import { memberService } from '../services/api';
import { validateMemberForm, trimWhitespace } from '../utils/validation';

function CreateMember() {
  const navigate = useNavigate();
  const location = useLocation();
  const { id } = useParams();
  const isEditMode = !!id;
  const [formData, setFormData] = useState({
    name: '',
    email: '',
  });
  const [originalEmail, setOriginalEmail] = useState('');
  const [formErrors, setFormErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [loadingMember, setLoadingMember] = useState(isEditMode);
  const [emailStatus, setEmailStatus] = useState({ checking: false, available: null });

  useEffect(() => {
    if (isEditMode) {
      // Try to get member data from navigation state first
      if (location.state?.member) {
        const email = location.state.member.email || '';
        setFormData({
          name: location.state.member.name || '',
          email: email,
        });
        setOriginalEmail(email);
        setLoadingMember(false);
      } else {
        loadMember();
      }
    }
  }, [id, location.state]);

  const loadMember = async () => {
    try {
      setLoadingMember(true);
      // Fetch all members to find the one with matching ID
      const response = await memberService.listMembers({ limit: 1000 });
      const members = response.data.members || [];
      const member = members.find(m => m.id === parseInt(id));

      if (member) {
        setFormData({
          name: member.name || '',
          email: member.email || '',
        });
        setOriginalEmail(member.email || '');
      } else {
        toast.error('Member not found');
        navigate('/members');
      }
    } catch (err) {
      const errorMessage = err.response?.data?.error?.message || err.response?.data?.error || 'Failed to load member';
      toast.error(errorMessage);
      navigate('/members');
    } finally {
      setLoadingMember(false);
    }
  };

  // Debounced email check
  useEffect(() => {
    const email = trimWhitespace(formData.email);

    // Reset status if empty or same as original
    if (!email || (isEditMode && email === originalEmail)) {
      setEmailStatus({ checking: false, available: null });
      setFormErrors(prev => ({ ...prev, email: null }));
      return;
    }

    const timer = setTimeout(async () => {
      setEmailStatus({ checking: true, available: null });
      try {
        const result = await memberService.checkEmail(email);
        setEmailStatus({ checking: false, available: result.available });
        if (!result.available) {
          setFormErrors(prev => ({ ...prev, email: 'Email is already taken' }));
        } else {
          setFormErrors(prev => ({ ...prev, email: null }));
        }
      } catch (err) {
        console.error('Email check failed', err);
        setEmailStatus({ checking: false, available: null });
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [formData.email, isEditMode, originalEmail]);

  const handleChange = (e) => {
    const value = e.target.value;
    const name = e.target.name;

    // Clear error for this field when user starts typing
    if (formErrors[name]) {
      setFormErrors({
        ...formErrors,
        [name]: null
      });
    }

    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Trim whitespace from all fields
    const trimmedData = {
      name: trimWhitespace(formData.name),
      email: trimWhitespace(formData.email),
    };

    // Validate form
    const validation = validateMemberForm(trimmedData);
    if (!validation.isValid) {
      setFormErrors(validation.errors);
      toast.error('Please fix the form errors');
      return;
    }

    // Check unique email status again before submitting
    if (trimmedData.email !== originalEmail && emailStatus.available === false) {
      setFormErrors(prev => ({ ...prev, email: 'Email is already taken' }));
      toast.error('Email is already taken');
      return;
    }

    setLoading(true);
    // Be careful not to clear errors if we want to keep them, but here we assume validation passed
    // setFormErrors({}); 

    try {
      if (isEditMode) {
        await memberService.updateMember(id, trimmedData);
        toast.success('Member updated successfully!');
      } else {
        await memberService.createMember(trimmedData);
        toast.success('Member created successfully!');
        setFormData({ name: '', email: '' });
        setOriginalEmail('');
      }

      setTimeout(() => {
        navigate('/members');
      }, 1000);
    } catch (err) {
      const errorMessage = err.response?.data?.error?.message || err.response?.data?.error || `Failed to ${isEditMode ? 'update' : 'create'} member`;
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  if (loadingMember) {
    return (
      <div className="row justify-content-center">
        <div className="col-md-6">
          <div className="text-center">
            <div className="spinner-border" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="row justify-content-center">
      <div className="col-md-6">
        <h2>{isEditMode ? 'Edit Member' : 'Add New Member'}</h2>

        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label htmlFor="name" className="form-label">
              Name <span className="text-danger">*</span>
            </label>
            <input
              type="text"
              className={`form-control ${formErrors.name ? 'is-invalid' : ''}`}
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
            />
            {formErrors.name && (
              <div className="invalid-feedback">{formErrors.name}</div>
            )}
          </div>

          <div className="mb-3">
            <label htmlFor="email" className="form-label">
              Email <span className="text-danger">*</span>
            </label>
            <div className="position-relative">
              <input
                type="email"
                className={`form-control ${formErrors.email ? 'is-invalid' : ''}`}
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
              />
              {emailStatus.checking && (
                <div className="position-absolute end-0 top-50 translate-middle-y me-2">
                  <div className="spinner-border spinner-border-sm text-secondary" role="status">
                    <span className="visually-hidden">Checking...</span>
                  </div>
                </div>
              )}
              {formErrors.email && (
                <div className="invalid-feedback">{formErrors.email}</div>
              )}
            </div>
          </div>

          <div className="d-flex gap-2">
            <button type="submit" className="btn btn-primary" disabled={loading || (emailStatus.checking)}>
              {loading ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  {isEditMode ? 'Updating...' : 'Creating...'}
                </>
              ) : (
                isEditMode ? 'Update Member' : 'Create Member'
              )}
            </button>
            <button
              type="button"
              className="btn btn-outline-secondary"
              onClick={() => navigate('/members')}
              disabled={loading}
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CreateMember;
